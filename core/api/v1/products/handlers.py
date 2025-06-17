import uuid

from django.http import Http404
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from pydantic import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.schemas.pagination import (
    PaginationIn,
    PaginationOut,
)
from core.api.schemas.response_schemas import (
    ApiResponse,
    ListResponsePayload,
)
from core.api.utils.response_builder import build_api_response
from core.api.v1.products.schemas.filters import OrderFilter
from core.api.v1.products.schemas.schemas import OrderCreate
from core.apps.common.exceptions.base_exception import ServiceException
from core.apps.common.exceptions.orders_exceptions.order_exc import OrderNotFoundException
from core.apps.products.models import Order
from core.apps.products.serializers import (
    AdminOrderSerializer,
    OrderUpdateSerializer,
    UserOrderSerializer,
)
from core.apps.products.services.order_service import OrderBaseService
from core.apps.products.tasks import send_order_creation_telegram_message
from core.project.containers import get_container
from core.project.permissions import (
    IsAdminUser,
    IsResourceOwner,
)


@extend_schema(tags=["Orders"])
class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Получить все заказы",
        description="Получает список всех заказов.",
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Поиск по описанию заказа.",
                required=False,
            ),
            OpenApiParameter(
                name="offset",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Смещение для пагинации.",
                required=False,
                default=0,
            ),
            OpenApiParameter(
                name="limit",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Лимит элементов для пагинации.",
                required=False,
                default=10,
            ),
        ],
        responses={
            200: ApiResponse[ListResponsePayload[AdminOrderSerializer | UserOrderSerializer]],
        },
        operation_id="list_all_orders",
    )
    def get(self, request: Request) -> Response:
        try:
            filters = OrderFilter.model_validate(
                request.query_params.dict(),
            )
            pagination_in = PaginationIn.model_validate(
                request.query_params.dict(),
            )
        except ValidationError as e:
            return build_api_response(
                message="Ошибка валидации параметров запроса",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=e.errors(),
            )
        except Exception as e:
            return build_api_response(
                message=f"Непредвиденная ошибка при обработке запроса: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors=[{"detail": str(e)}],
            )

        container = get_container()
        service: OrderBaseService = container.resolve(OrderBaseService)

        authenticated_user_id = request.user.id
        is_admin_user = request.user.is_staff

        user_id_for_service = authenticated_user_id if not is_admin_user else None

        orders = service.get_order_list(
            user_id=user_id_for_service,
            is_admin=is_admin_user,
            filters=filters,
            pagination_in=pagination_in,
        )

        orders_count = service.get_order_count(
            user_id=user_id_for_service,
            is_admin=is_admin_user,
            filters=filters,
        )

        pagination_out = PaginationOut(
            offset=pagination_in.offset,
            limit=pagination_in.limit,
            total=orders_count,
        )

        if is_admin_user:
            serializer = AdminOrderSerializer(orders, many=True)
        else:
            serializer = UserOrderSerializer(orders, many=True)

        return build_api_response(
            message="Заказы успешно получены",
            status_code=status.HTTP_200_OK,
            data=ListResponsePayload(
                items=serializer.data,
                pagination=pagination_out,
            ),
        )

    @extend_schema(
        summary="Создать новый заказ",
        description="Создаёт новый заказ с предоставленными данными.",
        request=OrderCreate,
        responses={
            201: AdminOrderSerializer,
            400: ApiResponse[None],
            500: ApiResponse[None],
        },
        operation_id="create_order",
    )
    def post(
        self,
        request: Request,
    ) -> Response:
        container = get_container()
        service = container.resolve(OrderBaseService)

        try:
            parsed_data = OrderCreate.model_validate(request.data)

            order_user_id = None
            if request.user.is_authenticated:
                if request.user.is_staff:
                    order_user_id = parsed_data.user_id if parsed_data.user_id else request.user.id
                else:
                    order_user_id = request.user.id
            else:
                return build_api_response(
                    message="Для создания заказа требуется аутентификация.",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

            if not order_user_id:
                return build_api_response(
                    message="Не удалось определить пользователя для создания заказа.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            order: Order = service.create_order(
                user_id=order_user_id,
                product_id=parsed_data.product_id,
                description=parsed_data.description,
            )

            if request.user.is_staff:
                serializer = AdminOrderSerializer(order)
            else:
                serializer = UserOrderSerializer(order)

            user = order.user

            send_order_creation_telegram_message.delay(telegram_id=user.telegram_id)

            return build_api_response(
                message="Заказ успешно создан",
                status_code=status.HTTP_201_CREATED,
                data=serializer.data,
            )
        except ValidationError as e:
            return build_api_response(
                message="Ошибка валидации входящих данных",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=e.errors(),
            )
        except ServiceException as e:
            return build_api_response(
                message=e.detail,
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=[{"detail": str(e)}],
            )
        except Exception as e:
            return build_api_response(
                message=f"Непредвиденная ошибка при обработке запроса: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors=[{"detail": str(e)}],
            )


@extend_schema(tags=["Orders"])
class OrderDetailActionView(APIView):

    def get_permissions(self):
        """
        Возвращает список разрешений в зависимости от HTTP-метода запроса.
        """
        if self.request.method in [
            "GET",
            "PUT",
            "PATCH",
        ]:
            return [IsAuthenticated(), IsResourceOwner()]
        elif self.request.method in [
            "DELETE",
        ]:
            return [IsAdminUser()]
        return super().get_permissions()

    def get_order_object(self, order_id: uuid.UUID) -> Order:
        container = get_container()
        service: OrderBaseService = container.resolve(OrderBaseService)
        user_id_for_service = None if self.request.user.is_staff else self.request.user.id

        try:
            order = service.get_order_by_id(
                order_id=order_id,
                user_id=user_id_for_service,
            )
        except OrderNotFoundException:
            raise Http404("Заказ не найден или у вас нет доступа к нему.")
        except Exception as e:
            raise Http404(f"Ошибка при получении заказа {e}.")

        self.check_object_permissions(self.request, order)

        return order

    @extend_schema(
        summary="Получить детали заказа по UUID",
        description="Позволяет администратору получить любой заказ, а владельцу - только свой заказ.",
        responses={
            200: UserOrderSerializer,
            404: ApiResponse[None],
            500: ApiResponse[None],
        },
        operation_id="retrieve_order_by_id",
    )
    def get(self, request: Request, order_id: uuid.UUID) -> Response:
        try:
            order = self.get_order_object(order_id)
            if request.user.is_staff:
                serializer = AdminOrderSerializer(order)
            else:
                serializer = UserOrderSerializer(order)

            return build_api_response(
                message="Заказ успешно получен",
                status_code=status.HTTP_200_OK,
                data=serializer.data,
            )
        except Http404 as e:
            return build_api_response(
                message=str(e),
                status_code=status.HTTP_404_NOT_FOUND,
                errors=[{"detail": str(e)}],
            )
        except ServiceException as e:
            return build_api_response(
                message=e.detail,
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=[{"detail": str(e)}],
            )
        except Exception as e:
            return build_api_response(
                message=f"Непредвиденная ошибка при обработке запроса: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors=[{"detail": str(e)}],
            )

    @extend_schema(
        summary="Обновить данные заказа (полное обновление)",
        description="Полностью обновляет данные заказа по его UUID. Все поля в теле запроса обязательны.",
        request=OrderUpdateSerializer,
        responses={
            200: ApiResponse[UserOrderSerializer],
            400: ApiResponse[None],
            404: ApiResponse[None],
            500: ApiResponse[None],
        },
        operation_id="update_order_description_by_id",
    )
    def put(self, request: Request, order_id: uuid.UUID) -> Response:
        try:
            order = self.get_order_object(order_id)

            serializer = OrderUpdateSerializer(
                data=request.data,
                partial=False,
            )
            serializer.is_valid(raise_exception=True)

            container = get_container()
            service: OrderBaseService = container.resolve(OrderBaseService)

            updated_order = service.update_order(
                order_id=order.id,
                data=serializer.validated_data,
            )

            if request.user.is_staff:
                response_serializer = AdminOrderSerializer(updated_order)
            else:
                response_serializer = UserOrderSerializer(updated_order)

            return build_api_response(
                message="Заказ успешно обновлен",
                status_code=status.HTTP_200_OK,
                data=response_serializer.data,
            )
        except Http404 as e:
            return build_api_response(
                message=str(e),
                status_code=status.HTTP_404_NOT_FOUND,
                errors=[{"detail": str(e)}],
            )
        except ServiceException as e:
            return build_api_response(
                message=e.detail,
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=[{"detail": str(e)}],
            )
        except Exception as e:
            return build_api_response(
                message=f"Непредвиденная ошибка при обработке запроса: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors=[{"detail": str(e)}],
            )

    @extend_schema(
        summary="Обновить данные заказа (частичное обновление)",
        description="Частично обновляет данные заказа по его UUID. Все поля в теле запроса обязательны.",
        request=OrderUpdateSerializer,
        responses={
            200: ApiResponse[UserOrderSerializer],
            400: ApiResponse[None],
            404: ApiResponse[None],
            500: ApiResponse[None],
        },
        operation_id="partial_update_order_description_by_id",
    )
    def patch(self, request: Request, order_id: uuid.UUID) -> Response:
        try:
            order = self.get_order_object(order_id)

            serializer = OrderUpdateSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            container = get_container()
            service: OrderBaseService = container.resolve(OrderBaseService)

            updated_order = service.update_order(
                order_id=order.id,
                data=serializer.validated_data,
            )

            if request.user.is_staff:
                response_serializer = AdminOrderSerializer(updated_order)
            else:
                response_serializer = UserOrderSerializer(updated_order)

            return build_api_response(
                message="Заказ успешно обновлен",
                status_code=status.HTTP_200_OK,
                data=response_serializer.data,
            )
        except Http404 as e:
            return build_api_response(
                message=str(e),
                status_code=status.HTTP_404_NOT_FOUND,
                errors=[{"detail": str(e)}],
            )
        except ServiceException as e:
            return build_api_response(
                message=e.detail,
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=[{"detail": str(e)}],
            )
        except Exception as e:
            return build_api_response(
                message=f"Непредвиденная ошибка при обработке запроса: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors=[{"detail": str(e)}],
            )

    @extend_schema(
        summary="Мягкое удаление заказа",
        description="Помечает заказа как удаленного (soft delete) по его UUID, делая его неактивным.",
        responses={
            204: UserOrderSerializer,
            404: ApiResponse[None],
            500: ApiResponse[None],
        },
        tags=["Admin"],
        operation_id="soft_delete_order_by_id",
    )
    def delete(self, request: Request, order_id: uuid.UUID) -> Response:
        try:
            order = self.get_order_object(order_id)

            container = get_container()
            service: OrderBaseService = container.resolve(OrderBaseService)

            deleted_order = service.soft_delete_order(
                order_id=order.id,
            )

            if request.user.is_staff:
                response_serializer = AdminOrderSerializer(deleted_order)
            else:
                response_serializer = UserOrderSerializer(deleted_order)

            return build_api_response(
                data=response_serializer.data,
                message="Заказ успешно удален",
                status_code=status.HTTP_200_OK,
            )
        except Http404 as e:
            return build_api_response(
                message=str(e),
                status_code=status.HTTP_404_NOT_FOUND,
                errors=[{"detail": str(e)}],
            )
        except ServiceException as e:
            return build_api_response(
                message=e.detail,
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=[{"detail": str(e)}],
            )
        except Exception as e:
            return build_api_response(
                message=f"Непредвиденная ошибка при обработке запроса: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors=[{"detail": str(e)}],
            )

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from pydantic import ValidationError

from core.api.v1.products.schemas.schemas import OrderCreate
from core.api.v1.products.schemas.filters import OrderFilter
from core.apps.products.services.order_service import OrderBaseService
from core.apps.products.serializers import (
    UserOrderSerializer,
    AdminOrderSerializer,
)

from core.api.schemas.pagination import (
    PaginationIn,
    PaginationOut,
)
from core.api.schemas.response_schemas import (
    ApiResponse,
    ListResponsePayload,
)

from core.project.permissions import HasActiveSubscription  # Ваш кастомный permission
from core.apps.common.exceptions.base_exception import ServiceException
from core.api.utils.response_builder import build_api_response
from core.project.containers import get_container
from rest_framework.permissions import IsAuthenticated


class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated, HasActiveSubscription]

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
        tags=["Orders"],
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
        tags=["Orders"],
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

            order = service.create_order(
                user_id=order_user_id,
                product_id=parsed_data.product_id,
                description=parsed_data.description,
            )

            if request.user.is_staff:
                serializer = AdminOrderSerializer(order)
            else:
                serializer = UserOrderSerializer(order)

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

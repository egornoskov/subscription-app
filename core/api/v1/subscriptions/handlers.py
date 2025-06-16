import uuid

from django.http import Http404
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from pydantic import ValidationError
from rest_framework import (
    status,
)
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
from core.api.v1.subscriptions.schemas.filters import SubscriptionFilter
from core.api.v1.subscriptions.schemas.schemas import SubscriptionCreate
from core.apps.common.exceptions.base_exception import ServiceException
from core.apps.common.exceptions.subs_exception.subs_exc import SubscriptionNotFoundException
from core.apps.subscriptions.models import Subscription
from core.apps.subscriptions.serializers import SubscriptionSerializer
from core.apps.subscriptions.services.base_service import SubscriptionBaseService
from core.project.containers import get_container
from core.project.permissions import (
    IsAccountActivated,
    IsAdminUser,
)


class SubscriptionsListCreateView(APIView):
    permission_classes = [IsAccountActivated, IsAuthenticated]

    @extend_schema(
        summary="Получить все подписки",
        description="Получает список всех подписок.",
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Поиск по названию тарифа подписки.",
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
            200: ApiResponse[ListResponsePayload[SubscriptionSerializer]],
        },
        tags=["Subscriptions"],
        operation_id="list_all_subscriptions",
    )
    def get(self, request: Request) -> Response:
        container = get_container()
        service: SubscriptionBaseService = container.resolve(SubscriptionBaseService)

        try:
            filters = SubscriptionFilter.model_validate(
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

        authenticated_user_id = request.user.id
        is_admin_user = request.user.is_staff

        subscriptions = service.get_subscription_list(
            user_id=authenticated_user_id,
            is_admin=is_admin_user,
            filters=filters,
            pagination_in=pagination_in,
        )

        subscriptions_count = service.get_subscription_count(
            user_id=authenticated_user_id,
            is_admin=is_admin_user,
            filters=filters,
        )

        pagination_out = PaginationOut(
            offset=pagination_in.offset,
            limit=pagination_in.limit,
            total=subscriptions_count,
        )

        subscriptions_data = SubscriptionSerializer(subscriptions, many=True).data

        return build_api_response(
            data=ListResponsePayload(
                items=subscriptions_data,
                pagination=pagination_out,
            ),
        )

    @extend_schema(
        summary="Создать новую подписку",
        description="Создаёт новую подписку с предоставленными данными.",
        request=SubscriptionCreate,
        responses={
            201: SubscriptionSerializer,
            400: ApiResponse[None],
            500: ApiResponse[None],
        },
        tags=["Subscriptions"],
        operation_id="create_subscription",
    )
    def post(
        self,
        request: Request,
    ) -> Response:
        container = get_container()
        service: SubscriptionBaseService = container.resolve(SubscriptionBaseService)

        try:
            parsed_data = SubscriptionCreate.model_validate(request.data)

            if request.user.is_staff:
                sub_user_id = parsed_data.user_id if parsed_data.user_id is not None else request.user.id
            else:
                sub_user_id = request.user.id

            if not sub_user_id:
                return build_api_response(
                    message="Не удалось определить пользователя для создания заказа.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            subscription = service.create_subscription(
                user_id=sub_user_id,
                tariff_id=parsed_data.tariff_id,
                month_duration=parsed_data.month_duration,
            )

            serializer = SubscriptionSerializer(subscription)

            return build_api_response(
                message="Подписка успешно создана",
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


class SubscriptionDetailActionsView(APIView):

    def get_permissions(self):
        """
        Возвращает список разрешений в зависимости от HTTP-метода запроса.
        """
        if self.request.method in [
            "GET",
            "PUT",
            "PATCH",
        ]:
            return [IsAuthenticated()]
        elif self.request.method in [
            "DELETE",
        ]:
            return [IsAdminUser()]
        return super().get_permissions()

    def get_subscription_object(self, sub_id: uuid.UUID) -> Subscription:
        container = get_container()
        service: SubscriptionBaseService = container.resolve(SubscriptionBaseService)
        user_id_for_service = None if self.request.user.is_staff else self.request.user.id

        try:
            subscription = service.get_subscription_by_id(
                sub_id=sub_id,
                user_id=user_id_for_service,
            )
        except SubscriptionNotFoundException:
            raise Http404("Подписка не найдена или у вас нет доступа к ней.")
        except Exception as e:
            raise Http404(f"Ошибка при получении заказа {e}.")

        self.check_object_permissions(self.request, subscription)

        return subscription

    @extend_schema(
        summary="Получить подписку по UUID",
        description="Получает детальную информацию о подписке, используя её UUID.",
        parameters=[
            OpenApiParameter(
                name="subscription_uuid",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="UUID Подписки.",
                required=True,
            ),
        ],
        responses={
            200: SubscriptionSerializer,
            404: ApiResponse[None],
            500: ApiResponse[None],
        },
        tags=["Subscriptions"],
        operation_id="retrieve_subscription_by_id",
    )
    def get(self, request: Request, subscription_uuid: uuid.UUID) -> Response:
        try:
            subscription = self.get_subscription_object(sub_id=subscription_uuid)
            subscription_data = SubscriptionSerializer(subscription).data

            return build_api_response(
                data=subscription_data,
                status_code=status.HTTP_200_OK,
            )
        except ServiceException as e:
            return build_api_response(
                message=e.detail,
                status_code=status.HTTP_404_NOT_FOUND,
                errors=[{"detail": str(e)}],
            )
        except Exception as e:
            return build_api_response(
                message=f"Непредвиденная ошибка при обработке запроса: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors=[{"detail": str(e)}],
            )

    @extend_schema(
        summary="Обновить данные подписки (полное обновление)",
        description="Полностью обновляет данные подписки по его UUID. Все поля в теле запроса обязательны.",
        request=SubscriptionSerializer,
        responses={
            200: ApiResponse[SubscriptionSerializer],
            400: ApiResponse[None],
            404: ApiResponse[None],
            500: ApiResponse[None],
        },
        tags=["Subscriptions"],
        operation_id="update_subscription",
    )
    def put(self, request: Request, subscription_uuid: uuid.UUID) -> Response:
        container = get_container()
        service: SubscriptionBaseService = container.resolve(SubscriptionBaseService)

        subscription = self.get_subscription_object(sub_id=subscription_uuid)

        try:
            serializer = SubscriptionSerializer(
                data=request.data,
                partial=False,
            )
            serializer.is_valid(raise_exception=True)

            tariff_obj = serializer.validated_data.get("tariff")
            end_date = serializer.validated_data.get("end_date")

            updated_subscription = service.update_subscription(
                sub_uuid=subscription.id,
                tariff=tariff_obj,
                end_date=end_date,
            )

            updated_subscription_data = SubscriptionSerializer(updated_subscription).data

            return build_api_response(
                data=updated_subscription_data,
                status_code=status.HTTP_200_OK,
            )
        except ServiceException as e:
            return build_api_response(
                message=e.detail,
                status_code=e.status_code,
                errors=[{"detail": str(e)}],
            )
        except Exception as e:
            return build_api_response(
                message=f"Непредвиденная ошибка при обработке запроса: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors=[{"detail": str(e)}],
            )

    @extend_schema(
        summary="Частичное обновление данных подписки",
        description=(
            "Частично обновляет данные подписки по его UUID. "
            "Позволяет отправлять только те поля, которые необходимо изменить."
        ),
        request=SubscriptionSerializer,
        responses={
            200: ApiResponse[SubscriptionSerializer],
            400: ApiResponse[None],
            404: ApiResponse[None],
            500: ApiResponse[None],
        },
        tags=["Subscriptions"],
        operation_id="partial_update_subscriptions",
    )
    def patch(self, request: Request, subscription_uuid: uuid.UUID) -> Response:
        container = get_container()
        service: SubscriptionBaseService = container.resolve(SubscriptionBaseService)

        subscription = self.get_subscription_object(sub_id=subscription_uuid)

        try:
            serializer = SubscriptionSerializer(
                data=request.data,
                partial=False,
            )
            serializer.is_valid(raise_exception=True)

            tariff_obj = serializer.validated_data.get("tariff")
            end_date = serializer.validated_data.get("end_date")

            updated_subscription = service.partial_update_subscription(
                sub_uuid=subscription.id,
                tariff=tariff_obj,
                end_date=end_date,
            )

            updated_subscription_data = SubscriptionSerializer(updated_subscription).data

            return build_api_response(
                data=updated_subscription_data,
                status_code=status.HTTP_200_OK,
            )

        except ServiceException as e:
            return build_api_response(
                message=e.detail,
                status_code=e.status_code,
                errors=[{"detail": str(e)}],
            )
        except Exception as e:
            return build_api_response(
                message=f"Непредвиденная ошибка при обработке запроса: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors=[{"detail": str(e)}],
            )

    @extend_schema(
        summary="Мягкое удаление подписки",
        description="Помечает подписки как удаленного (soft delete) по его UUID, делая его неактивным.",
        responses={
            200: None,
            404: ApiResponse[None],
            500: ApiResponse[None],
        },
        tags=["Subscriptions"],
        operation_id="soft_delete_subscription",
    )
    def delete(self, request: Request, subscription_uuid: uuid.UUID) -> Response:
        container = get_container()
        service: SubscriptionBaseService = container.resolve(SubscriptionBaseService)

        subscription = self.get_subscription_object(sub_id=subscription_uuid)

        try:

            delted_subscription = service.soft_delete_subscription(sub_id=subscription.id)
            return build_api_response(
                data=SubscriptionSerializer(delted_subscription).data,
                status_code=status.HTTP_200_OK,
            )
        except ServiceException as e:
            return build_api_response(
                message=e.detail,
                status_code=e.status_code,
                errors=[{"detail": str(e)}],
            )
        except Exception as e:
            return build_api_response(
                message=f"Непредвиденная ошибка при обработке запроса: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors=[{"detail": str(e)}],
            )


@extend_schema(tags=["Admin"])
class HardDeleteSubscriptionView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="Полное удаление подписки",
        description=(
            "Полностью и безвозвратно удаляет подписки из базы данных по его UUID. "
            "Возможно только для подписок, уже помеченных как удаленные (soft-deleted)."
        ),
        responses={
            204: None,  # Изменено на 204 No Content, как для удаления
            404: ApiResponse[None],
            500: ApiResponse[None],
        },
        operation_id="hard_delete_subscription",
    )
    def delete(
        self,
        request: Request,
        subscription_id: uuid.UUID,
    ) -> Response:
        container = get_container()
        service: SubscriptionBaseService = container.resolve(SubscriptionBaseService)

        try:
            service.hard_delete_subscription(sub_id=subscription_id)

            return build_api_response(
                status_code=status.HTTP_204_OK,
                message="Подписка успешно удалена",
            )
        except ServiceException as e:
            return build_api_response(
                message=e.detail,
                status_code=e.status_code,
                errors=[{"detail": str(e)}],
            )
        except Exception as e:
            return build_api_response(
                message=f"Непредвиденная ошибка при обработке запроса: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors=[{"detail": str(e)}],
            )


@extend_schema(tags=["Admin"])
class ArchiveListSubscriptionView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="Получить все архивные подписки",
        description="Получает список всех архивных подписок.",
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Поиск по названию тарифа подписки.",
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
            200: ApiResponse[ListResponsePayload[SubscriptionSerializer]],
        },
        operation_id="list_archive_subscriptions",
    )
    def get(self, request: Request) -> Response:
        container = get_container()
        service: SubscriptionBaseService = container.resolve(SubscriptionBaseService)

        try:
            filters = SubscriptionFilter.model_validate(
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

        subscriptions = service.get_subscription_list_archive(
            filters=filters,
            pagination_in=pagination_in,
        )

        subscriptions_count = service.get_subscription_count_archive(
            filters=filters,
        )

        pagination_out = PaginationOut(
            offset=pagination_in.offset,
            limit=pagination_in.limit,
            total=subscriptions_count,
        )

        subscriptions_data = SubscriptionSerializer(subscriptions, many=True).data

        return build_api_response(
            data=ListResponsePayload(
                items=subscriptions_data,
                pagination=pagination_out,
            ),
        )

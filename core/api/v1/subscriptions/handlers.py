import uuid
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from pydantic import ValidationError
from rest_framework import (
    status,
)
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
from core.api.v1.subscriptions.schemas.schemas import SubscriptionCreate
from core.apps.common.exceptions.base_exception import ServiceException
from core.apps.subscriptions.serializers import SubscriptionSerializer
from core.project.containers import get_container
from core.apps.subscriptions.services.base_service import SubscriptionBaseService
from core.api.v1.subscriptions.schemas.filters import SubscriptionFilter


class SubscriptionsListCreateView(APIView):
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

        subscriptions = service.get_subscription_list(
            filters=filters,
            pagination_in=pagination_in,
        )

        subscriptions_count = service.get_subscription_count(
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
    def post(self, request: Request) -> Response:
        container = get_container()
        service: SubscriptionBaseService = container.resolve(SubscriptionBaseService)
        try:
            parsed_data = SubscriptionCreate.model_validate(request.data)

            subscription = service.create_subscription(
                user_id=parsed_data.user_id,
                tariff_id=parsed_data.tariff_id,
                month_duration=parsed_data.month_duration,
            )

            response_data = SubscriptionSerializer(subscription).data

            return build_api_response(
                data=response_data,
                status_code=status.HTTP_201_CREATED,
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
        container = get_container()
        service: SubscriptionBaseService = container.resolve(SubscriptionBaseService)

        try:
            subscription = service.get_subscription_by_id(subscription_uuid)
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

        try:
            serializer = SubscriptionSerializer(
                data=request.data,
                partial=False,
            )
            serializer.is_valid(raise_exception=True)

            tariff_obj = serializer.validated_data.get("tariff")
            end_date = serializer.validated_data.get("end_date")

            updated_subscription = service.update_subscription(
                sub_uuid=subscription_uuid,
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

        try:
            serializer = SubscriptionSerializer(
                data=request.data,
                partial=False,
            )
            serializer.is_valid(raise_exception=True)

            tariff_obj = serializer.validated_data.get("tariff")
            end_date = serializer.validated_data.get("end_date")

            updated_subscription = service.partial_update_subscription(
                sub_uuid=subscription_uuid,
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
            204: None,
            404: ApiResponse[None],
            500: ApiResponse[None],
        },
        tags=["Subscriptions"],
        operation_id="soft_delete_subscription",
    )
    def delete(self, request: Request, subscription_uuid: uuid.UUID) -> Response:
        container = get_container()
        service: SubscriptionBaseService = container.resolve(SubscriptionBaseService)

        try:
            service.soft_delete_subscription(sub_id=subscription_uuid)
            return build_api_response(
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

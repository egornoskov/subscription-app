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
from core.api.v1.tariff.schemas.filters import TariffFilter
from core.api.v1.tariff.schemas.schemas import (
    TariffCreateSchema,
    TariffUpdateSchema,
)
from core.apps.common.exceptions.base_exception import ServiceException
from core.apps.common.exceptions.tariff_custom_exceptions.tariff_exc import TariffNotFoundError
from core.apps.tariff.serializers import TariffSerializer
from core.apps.tariff.services.tariff_base_service import TariffBaseService
from core.project.containers import get_container
from core.project.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated


class TariffListCreateView(APIView):

    def get_permissions(self):
        """
        Возвращает список разрешений в зависимости от HTTP-метода запроса.
        """
        if self.request.method in ["GET"]:
            return [IsAuthenticated()]
        elif self.request.method in ["POST"]:
            return [IsAdminUser()]
        return super().get_permissions()

    @extend_schema(
        summary="Получить все тарифы подписок",
        description="Получает список всех тарифов подписок.",
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Поиск по названию подписки.",
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
            200: ApiResponse[ListResponsePayload[TariffSerializer]],
        },
        tags=["Tariffs"],
        operation_id="list_all_tariffs",
    )
    def get(
        self,
        request: Request,
    ) -> Response:
        try:
            filters = TariffFilter.model_validate(
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
        service: TariffBaseService = container.resolve(TariffBaseService)

        tariffs = service.get_tariff_list(
            filters=filters,
            pagination_in=pagination_in,
        )
        tariffs_count: int = service.get_tariff_count(
            filters=filters,
        )
        pagination_out = PaginationOut(
            offset=pagination_in.offset,
            limit=pagination_in.limit,
            total=tariffs_count,
        )
        tariffs_data = TariffSerializer(tariffs, many=True).data

        return build_api_response(
            data=ListResponsePayload(
                items=tariffs_data,
                pagination=pagination_out,
            ),
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Создать новый тариф",
        description="Создаёт новый тариф с предоставленными данными.",
        request=TariffCreateSchema,
        responses={
            201: ApiResponse[TariffSerializer],
            400: ApiResponse[None],
            500: ApiResponse[None],
        },
        tags=["Admin"],
        operation_id="create_tariff",
    )
    def post(
        self,
        request: Request,
    ) -> Response:
        container = get_container()
        service: TariffBaseService = container.resolve(TariffBaseService)

        try:
            tariff_data = TariffCreateSchema.model_validate(request.data)
            new_tariff = service.create_tariff(
                name=tariff_data.name,
                price=tariff_data.price,
            )
            new_tariff_data = TariffSerializer(new_tariff).data
            return build_api_response(
                data=new_tariff_data,
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
                status_code=e.status_code,
                errors=[{"detail": str(e)}],
            )
        except Exception as e:
            return build_api_response(
                message=f"Непредвиденная ошибка при обработке запроса: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors=[{"detail": str(e)}],
            )


class TariffDetailActionsView(APIView):

    def get_permissions(self):
        """
        Возвращает список разрешений в зависимости от HTTP-метода запроса.
        """
        if self.request.method in ["GET"]:
            return [IsAuthenticated()]
        elif self.request.method in [
            "DELETE",
            "PUT",
            "PATCH",
        ]:
            return [IsAdminUser()]
        return super().get_permissions()

    @extend_schema(
        summary="Получить тариф по UUID",
        description="Получает детальную информацию о тарифе, используя его UUID.",
        parameters=[
            OpenApiParameter(
                name="tariff_uuid",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="UUID Тарифа.",
                required=True,
            ),
        ],
        responses={
            200: ApiResponse[TariffSerializer],
            404: ApiResponse[None],
            500: ApiResponse[None],
        },
        tags=["Tariffs"],
        operation_id="retrieve_tariff_by_id",
    )
    def get(
        self,
        request: Request,
        tariff_uuid: uuid.UUID,
    ) -> Response:
        container = get_container()
        service = container.resolve(TariffBaseService)

        try:
            tariff = service.get_tariff_by_id(tariff_uuid=tariff_uuid)
            tariff_data = TariffSerializer(tariff).data
            return build_api_response(
                data=tariff_data,
                status_code=status.HTTP_200_OK,
            )
        except TariffNotFoundError as e:
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
        summary="Обновить данные тарифа (полное обновление)",
        description="Полностью обновляет данные тарифа по его UUID. Все поля в теле запроса обязательны.",
        request=TariffUpdateSchema,
        responses={
            200: ApiResponse[TariffSerializer],
            400: ApiResponse[None],
            404: ApiResponse[None],
            500: ApiResponse[None],
        },
        tags=["Tariffs"],
        operation_id="update_tariff",
    )
    def put(self, request: Request, tariff_uuid: uuid.UUID) -> Response:
        container = get_container()
        service = container.resolve(TariffBaseService)

        try:
            updated_data = TariffUpdateSchema.model_validate(request.data)

            updated_tariff = service.update_tariff(
                tariff_uuid=tariff_uuid,
                data_to_update=updated_data,
            )

            updated_tariff_data = TariffSerializer(updated_tariff).data

            return build_api_response(
                data=updated_tariff_data,
                status_code=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return build_api_response(
                message="Ошибка валидации данных запроса",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=e.errors(),
            )
        except TariffNotFoundError as e:
            return build_api_response(
                message=e.detail,
                status_code=e.status_code,
                errors=[{"detail": str(e)}],
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
        summary="Частичное обновление данных тарифа",
        description=(
            "Частично обновляет данные тарифа по его UUID. "
            "Позволяет отправлять только те поля, которые необходимо изменить."
        ),
        request=TariffUpdateSchema,
        responses={
            200: ApiResponse[TariffSerializer],
            400: ApiResponse[None],
            404: ApiResponse[None],
            500: ApiResponse[None],
        },
        tags=["Tariffs"],
        operation_id="partial_update_tariff",
    )
    def patch(
        self,
        request: Request,
        tariff_uuid: uuid.UUID,
    ) -> Response:
        container = get_container()
        service = container.resolve(TariffBaseService)

        try:
            data_to_update = TariffUpdateSchema.model_validate(
                request.data,
            )
            updated_tariff = service.partial_update_tariff(
                tariff_uuid=tariff_uuid,
                data_to_update=data_to_update,
            )
            updated_tariff_data = TariffSerializer(updated_tariff).data

            return build_api_response(
                data=updated_tariff_data,
                status_code=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return build_api_response(
                message="Ошибка валидации данных запроса",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=e.errors(),
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
        summary="Мягкое удаление тарифа",
        description="Помечает тарифа как удаленного (soft delete) по его UUID, делая его неактивным.",
        responses={
            200: TariffSerializer,
            404: ApiResponse[None],
            500: ApiResponse[None],
        },
        tags=["Admin"],
        operation_id="soft_delete_tariff",
    )
    def delete(
        self,
        request: Request,
        tariff_uuid: uuid.UUID,
    ) -> Response:

        container = get_container()
        service = container.resolve(TariffBaseService)

        try:
            tariff = service.soft_delete_tariff(tariff_uuid=tariff_uuid)
            return build_api_response(
                status_code=status.HTTP_200_OK,
                data=TariffSerializer(tariff).data,
            )
        except TariffNotFoundError as e:
            return build_api_response(
                message=e.detail,
                status_code=e.status_code,
                errors=[{"detail": str(e)}],
            )
        except ServiceException as e:
            return build_api_response(
                message=e.detail,
                status_code=e.status_code,
                errors=[{"detail": str(e)}],
            )


@extend_schema(tags=["Admin"])
class TariffArchiveListView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="Получить архив тарифов",
        description="Получает список архивных тарифов.",
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Поиск по названию подписки.",
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
            200: ApiResponse[ListResponsePayload[TariffSerializer]],
        },
        operation_id="list_all_tariffs_archive",
    )
    def get(
        self,
        request: Request,
    ) -> Response:
        try:
            filters = TariffFilter.model_validate(
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
        service: TariffBaseService = container.resolve(TariffBaseService)

        tariffs = service.get_tariff_list_archive(
            filters=filters,
            pagination_in=pagination_in,
        )
        tariffs_count: int = service.get_tariffs_count_archive(
            filters=filters,
        )
        pagination_out = PaginationOut(
            offset=pagination_in.offset,
            limit=pagination_in.limit,
            total=tariffs_count,
        )
        tariffs_data = TariffSerializer(tariffs, many=True).data

        return build_api_response(
            data=ListResponsePayload(
                items=tariffs_data,
                pagination=pagination_out,
            ),
            status_code=status.HTTP_200_OK,
        )


@extend_schema(tags=["Admin"])
class HardDeleteTariffView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="Полное удаление тарифа",
        description=(
            "Полностью и безвозвратно удаляет тарифа из базы данных по его UUID. "
            "Возможно только для тарифов, уже помеченных как удаленные (soft-deleted)."
        ),
        responses={
            204: None,  # Изменено на 204 No Content, как для удаления
            404: ApiResponse[None],
            500: ApiResponse[None],
        },
        operation_id="hard_delete_tariff",
    )
    def delete(
        self,
        request: Request,
        tariff_uuid: uuid.UUID,
    ) -> Response:
        container = get_container()
        service: TariffBaseService = container.resolve(TariffBaseService)

        try:
            service.hard_delete_tariff(tariff_uuid=tariff_uuid)
            return build_api_response(
                status_code=status.HTTP_204_OK,
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

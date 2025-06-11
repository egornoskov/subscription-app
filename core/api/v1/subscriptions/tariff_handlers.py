from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from pydantic import ValidationError
from rest_framework import (
    generics,
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
from core.apps.subscription.serializers import TariffSerializer
from core.apps.subscription.services.tariff_base_service import TariffBaseService
from core.api.utils.response_builder import build_api_response
from core.api.v1.subscriptions.schemas.filters import TariffFilter
from core.project.containers import get_container


class TariffListView(APIView):
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
        service = container.resolve(TariffBaseService)

        tariffs = service.get_tariff_list(
            filters=filters,
            pagination_in=pagination_in,
        )
        tariffs_count = service.get_tariff_count(
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

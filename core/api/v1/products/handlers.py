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
from core.apps.products.services.base_order_service import OrderBaseService
from core.project.containers import get_container

from core.apps.products.serializers import UserOrderSerializer
from core.api.v1.products.schemas.filters import OrderFilter


class OrderListCreateView(APIView):

    def get(self, request: Request) -> Response:
        container = get_container()
        service = container.resolve(OrderBaseService)

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

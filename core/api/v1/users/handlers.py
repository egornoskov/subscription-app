from typing import Iterable

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from pydantic import ValidationError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.pagination import (
    PaginationIn,
    PaginationOut,
)
from core.api.utils import build_api_response
from core.api.v1.users.filters import UserFilter
from core.apps.user.models import User
from core.apps.user.serializers import UserSerializer
from core.apps.user.services.base_user_service import BaseUserService
from core.project.containers import get_container


class UserListView(APIView):
    @extend_schema(
        summary="Получить список пользователей",
        parameters=[
            OpenApiParameter(
                name="offset",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Количество элементов, которые нужно пропустить (смещение)",
                required=False,
                default=0,
            ),
            OpenApiParameter(
                name="limit",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Максимальное количество элементов для возврата",
                required=False,
                default=10,
            ),
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Поиск пользователей по имени",
                required=False,
            ),
            OpenApiParameter(
                name="email",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Поиск пользователей по электронной почте",
                required=False,
            ),
        ],
        responses={
            200: {
                "description": "Список пользователей успешно получен",
                "type": "object",
                "properties": {
                    "data": {"type": "array", "items": {"$ref": "#/components/schemas/UserSerializer"}},
                    "pagination": {
                        "type": "object",
                        "properties": {
                            "offset": {"type": "integer"},
                            "limit": {"type": "integer"},
                            "total": {"type": "integer"},
                        },
                    },
                },
            },
            400: {
                "description": "Ошибка валидации параметров запроса",
                "type": "object",
            },
            500: {
                "description": "Внутренняя ошибка сервера",
                "type": "object",
            },
        },
        tags=["Users"],
    )
    def get(
        self,
        request: Request,
    ) -> Response:
        try:
            filters = UserFilter.model_validate(request.query_params.dict())
            pagination_in = PaginationIn.model_validate(request.query_params.dict())
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
        service: BaseUserService = container.resolve(BaseUserService)

        users: Iterable[User] = service.get_users_list(
            filters=filters,
            pagination_in=pagination_in,
        )
        users_count: int = service.get_users_count(
            filters=filters,
        )

        serialized_users_data = UserSerializer(users, many=True).data

        pagination_out = PaginationOut(
            offset=pagination_in.offset,
            limit=pagination_in.limit,
            total=users_count,
        )

        return build_api_response(
            data={
                "items": serialized_users_data,
                "pagination": pagination_out.model_dump(exclude_none=True),
            },
            message="Список пользователей успешно получен",
            status_code=status.HTTP_200_OK,
        )

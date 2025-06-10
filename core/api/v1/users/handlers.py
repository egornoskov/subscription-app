from typing import Iterable
from uuid import UUID

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

from core.api.pagination import (
    PaginationIn,
    PaginationOut,
)
from core.api.response_schemas import (
    ApiResponse,
    ListResponsePayload,
)
from core.api.utils import build_api_response
from core.api.v1.users.filters import UserFilter
from core.apps.common.exceptions.user_custom_exceptions.base_exception import ServiceException
from core.apps.user.models import User
from core.apps.user.serializers import UserSerializer
from core.apps.user.services.base_user_service import BaseUserService
from core.project.containers import get_container


class UserListView(APIView):
    @extend_schema(
        summary="Получить всех активных пользователей",
        description="Получает список всех пользователей.",
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Поиск по имени, фамилии или email.",
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
            200: ApiResponse[ListResponsePayload[UserSerializer]],
        },
        tags=["Users"],
        operation_id="list_all_users",
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


class UserRetriveByIdView(generics.RetrieveAPIView):
    @extend_schema(
        summary="Получить пользователя по UUID",
        description="Получает детальную информацию о пользователе, используя его UUID.",
        parameters=[
            OpenApiParameter(
                name="user_uuid",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="UUID пользователя.",
                required=True,
            ),
        ],
        responses={
            200: ApiResponse[UserSerializer],
        },
        tags=["Users"],
        operation_id="retrieve_user_by_id",
    )
    def get(
        self,
        request: Request,
        user_uuid: UUID,
    ) -> Response:
        container = get_container()
        service: BaseUserService = container.resolve(BaseUserService)

        try:
            user = service.get_user_by_id(user_id=user_uuid)
            user_serialize_data = UserSerializer(user).data

            return build_api_response(
                data=user_serialize_data,
                message="Пользователь успешно получен",
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


class UserRetriveByEmailView(generics.RetrieveAPIView):
    @extend_schema(
        summary="Получить пользователя по Email",
        description="Получает детальную информацию о пользователе, используя его адрес электронной почты.",
        parameters=[
            OpenApiParameter(
                name="user_email",
                type={"type": "string", "format": "email"},
                location=OpenApiParameter.PATH,
                description="Адрес электронной почты пользователя.",
                required=True,
            ),
        ],
        responses={
            200: ApiResponse[UserSerializer],
        },
        tags=["Users"],
        operation_id="retrieve_user_by_email",
    )
    def get(
        self,
        request: Request,
        user_email: str,
    ) -> Response:
        container = get_container()
        service: BaseUserService = container.resolve(BaseUserService)

        try:
            user = service.get_user_by_email(user_email=user_email)
            user_serialize_data = UserSerializer(user).data

            return build_api_response(
                data=user_serialize_data,
                message="Пользователь успешно получен",
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

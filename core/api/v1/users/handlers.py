from typing import Iterable
from uuid import UUID

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

from core.api.schemas.pagination import (
    PaginationIn,
    PaginationOut,
)
from core.api.schemas.response_schemas import (
    ApiResponse,
    ListResponsePayload,
)
from core.api.utils.response_builder import build_api_response
from core.api.v1.users.schemas.filters import UserFilter
from core.api.v1.users.schemas.user_schemas import (
    UserCreateIn,
    UserUpdateIn,
)
from core.apps.common.exceptions.base_exception import ServiceException
from core.apps.common.exceptions.user_custom_exceptions.user_exc import UserNotFoundException
from core.apps.user.models import User
from core.apps.user.serializers import UserSerializer
from core.apps.user.services.base_user_service import BaseUserService
from rest_framework.permissions import IsAdminUser
from core.project.containers import get_container
from core.project.permissions import IsUserOwnerOrAdmin


@extend_schema(tags=["Admin"])
class UserListCreateView(APIView):
    permission_classes = [IsAdminUser]

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

    @extend_schema(
        summary="Создать нового пользователя",
        description="Создаёт нового пользователя с предоставленными данными.",
        request=UserCreateIn,
        responses={
            201: ApiResponse[UserSerializer],
            400: ApiResponse[None],
            500: ApiResponse[None],
        },
        operation_id="create_user",
    )
    def post(
        self,
        request: Request,
    ) -> Response:
        container = get_container()
        service = container.resolve(BaseUserService)

        try:
            user_data = UserCreateIn.model_validate(request.data)
            new_user = service.create_user(
                email=user_data.email,
                password=user_data.password,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                phone=user_data.phone,
            )
            new_user_data = UserSerializer(new_user).data
            return build_api_response(
                data=new_user_data,
                message="Пользователь успешно создан",
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


class UserDetailActionsView(APIView):
    def get_permissions(self):
        """
        Возвращает список разрешений в зависимости от HTTP-метода запроса.
        """
        if self.request.method in ["PUT", "PATCH"]:
            return [IsUserOwnerOrAdmin()]
        elif self.request.method in ["GET", "DELETE"]:
            return [IsAdminUser()]
        return super().get_permissions()

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
            404: ApiResponse[None],
            500: ApiResponse[None],
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

    @extend_schema(
        summary="Обновить данные пользователя (полное обновление)",
        description="Полностью обновляет данные пользователя по его UUID. Все поля в теле запроса обязательны.",
        request=UserUpdateIn,
        responses={
            200: ApiResponse[UserSerializer],
            400: ApiResponse[None],
            404: ApiResponse[None],
            500: ApiResponse[None],
        },
        tags=["Users"],
        operation_id="update_user_full",
    )
    def put(
        self,
        request: Request,
        user_uuid: UUID,
    ) -> Response:
        container = get_container()
        service = container.resolve(BaseUserService)

        try:
            user_data = UserUpdateIn.model_validate(request.data)
            updated_user = service.user_update_full(
                user_id=user_uuid,
                user_data=user_data,
            )
            updated_user_data = UserSerializer(updated_user).data

            return build_api_response(
                data=updated_user_data,
                message="Пользователь успешно обновлен",
                status_code=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return build_api_response(
                message="Ошибка валидации входящих данных",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=e.errors(),
            )
        except UserNotFoundException as e:
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
        summary="Частичное обновление данных пользователя",
        description=(
            "Частично обновляет данные пользователя по его UUID. "
            "Позволяет отправлять только те поля, которые необходимо изменить."
        ),
        request=UserUpdateIn,
        responses={
            200: ApiResponse[UserSerializer],
            400: ApiResponse[None],
            404: ApiResponse[None],
            500: ApiResponse[None],
        },
        tags=["Users"],
        operation_id="update_user_partial",
    )
    def patch(
        self,
        request: Request,
        user_uuid: UUID,
    ) -> Response:
        container = get_container()
        service = container.resolve(BaseUserService)

        try:
            user_data = UserUpdateIn.model_validate(request.data)
            updated_user = service.user_update_partial(
                user_id=user_uuid,
                user_data=user_data,
            )
            updated_user_data = UserSerializer(updated_user).data

            return build_api_response(
                data=updated_user_data,
                message="Пользователь успешно обновлен",
                status_code=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return build_api_response(
                message="Ошибка валидации входящих данных",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=e.errors(),
            )
        except UserNotFoundException as e:
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
        summary="Мягкое удаление пользователя",
        description="Помечает пользователя как удаленного (soft delete) по его UUID, делая его неактивным.",
        responses={
            204: None,
            404: ApiResponse[None],
            500: ApiResponse[None],
        },
        tags=["Users"],
        operation_id="soft_delete_user",
    )
    def delete(
        self,
        request: Request,
        user_uuid: UUID,
    ) -> Response:
        container = get_container()
        service = container.resolve(BaseUserService)

        try:
            service.soft_delete_user(user_id=user_uuid)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserNotFoundException as e:
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


@extend_schema(tags=["Admin"])
class UserHardDeleteView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="Полное удаление пользователя",
        description=(
            "Полностью и безвозвратно удаляет пользователя из базы данных по его UUID. "
            "Возможно только для пользователей, уже помеченных как удаленные (soft-deleted)."
        ),
        responses={
            204: None,  # Изменено на 204 No Content, как для удаления
            404: ApiResponse[None],
            500: ApiResponse[None],
        },
        operation_id="hard_delete_user",
    )
    def delete(self, request: Request, user_uuid: UUID) -> Response:
        container = get_container()
        service = container.resolve(BaseUserService)

        try:
            service.hard_delete_user(user_id=user_uuid)
            return Response(status=status.HTTP_204_NO_CONTENT)  # Изменено на 204 No Content
        except UserNotFoundException as e:
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


@extend_schema(tags=["Admin"])
class ArchivedUserListView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="Получить всех архивных пользователей",  # Изменено описание для ясности
        description="Получает список всех архивных пользователей.",  # Изменено описание
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
        operation_id="list_all_archived_users",  # Изменено operation_id
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

        users: Iterable[User] = service.get_all_users_archive(
            filters=filters,
            pagination_in=pagination_in,
        )
        users_count: int = service.get_users_count_archive(
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

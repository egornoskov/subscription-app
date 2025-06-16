from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.schemas.response_schemas import ApiResponse
from core.api.utils.response_builder import build_api_response
from core.apps.common.exceptions.base_exception import ServiceException
from core.apps.user.serializers import (
    UserRegistrationSerializer,
    UserSerializer,
)
from core.apps.user.services.base_user_service import BaseUserService
from core.project.containers import get_container


@method_decorator(csrf_exempt, name="dispatch")
class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Регистрация",
        description="Регистрирует нового пользователя с предоставленными данными.",
        request=UserRegistrationSerializer,
        responses={
            201: ApiResponse[UserSerializer],
            400: ApiResponse[None],
            500: ApiResponse[None],
        },
        tags=["v1"],
        operation_id="register_user",
    )
    def post(
        self,
        request: Request,
    ) -> Response:
        serializer = UserRegistrationSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)

            container = get_container()
            service = container.resolve(BaseUserService)

            new_user = service.create_user(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
                first_name=serializer.validated_data["first_name"],
                last_name=serializer.validated_data["last_name"],
                phone=serializer.validated_data["phone"],
            )

            new_user_data = UserSerializer(new_user).data

            return build_api_response(
                data=new_user_data,
                message="Пользователь успешно создан. Пожалуйста, активируйте аккаунт через телеграм бот.",
                status_code=status.HTTP_201_CREATED,
            )
        except DRFValidationError as e:
            return build_api_response(
                message="Ошибка валидации входящих данных",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=e.detail,
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


# class ActivateUserAPIView(APIView):
#     permission_classes = [IsBotApiKeyAuthenticated]

#     @extend_schema(
#         summary="Активация профиля через тг бота",
#         description="Активирует нового пользователя с предоставленными данными.",
#         request={
#             "application/json": {
#                 "type": "object",
#                 "properties": {
#                     "phone_number": {
#                         "type": "string",
#                         "example": "+79123456789",
#                         "description": "Номер телефона пользователя (включая код страны).",
#                     },
#                     "telegram_id": {
#                         "type": "integer",
#                         "example": 123456789,
#                         "description": "Уникальный ID пользователя в Telegram.",
#                     },
#                 },
#                 "required": ["phone_number", "telegram_id"],
#             }
#         },
#         responses={
#             201: ApiResponse[UserSerializer],
#             400: ApiResponse[None],
#             500: ApiResponse[None],
#         },
#         tags=["v1"],
#         operation_id="activate_user",
#     )
#     def post(self, request: Request) -> Response:
#         container = get_container()
#         service = container.resolve(BaseUserService)

#         phone_number = request.data.get("phone_number")
#         telegram_id = request.data.get("telegram_id")

#         if not phone_number or not telegram_id:
#             return build_api_response(
#                 message="Недостаточно данных для активации пользователя.",
#                 status_code=status.HTTP_400_BAD_REQUEST,
#             )

#         try:
#             was_inactive = service.activate_user_and_set_telegram_id(phone_number, telegram_id)
#             return build_api_response(
#                 message="Пользователь успешно активирован." if was_inactive else "Пользователь уже активен.",
#                 status_code=status.HTTP_200_OK,
#             )
#         except ServiceException as e:
#             return build_api_response(
#                 message=e.detail,
#                 status_code=e.status_code,
#                 errors=[{"detail": str(e)}],
#             )
#         except Exception as e:
#             return build_api_response(
#                 message=f"Непредвиденная ошибка при обработке запроса: {e}",
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 errors=[{"detail": str(e)}],
#             )

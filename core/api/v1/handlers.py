from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError as DRFValidationError

from core.api.schemas.response_schemas import ApiResponse
from core.api.utils.response_builder import build_api_response
from drf_spectacular.utils import extend_schema
from core.apps.common.exceptions.base_exception import ServiceException
from core.apps.user.serializers import UserSerializer, UserRegistrationSerializer
from core.apps.user.services.base_user_service import BaseUserService
from core.project.containers import get_container

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


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

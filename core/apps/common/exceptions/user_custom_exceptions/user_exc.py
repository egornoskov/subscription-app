import uuid

from rest_framework import status

from core.apps.common.exceptions.user_custom_exceptions.base_exception import ServiceException


class UserNotFoundException(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Пользователь не найден."

    def __init__(self, user_id: uuid.UUID = None):
        detail = self.default_detail
        if user_id:
            detail = f"Пользователь с ID '{user_id}' не найден."
        super().__init__(detail=detail, code="user_not_found")


class ValidationErrorAPI(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Ошибка валидации."
    default_code = "validation_error"

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if not isinstance(detail, dict):
            detail = {"non_field_errors": [detail]}
        super().__init__(detail=detail, code=code)


class UserEmailNotFoundException(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Пользователь не найден."

    def __init__(self, user_email: str):
        detail = self.default_detail
        if user_email:
            detail = f"Пользователь с ID '{user_email}' не найден."
        super().__init__(detail=detail, code="user_not_found")

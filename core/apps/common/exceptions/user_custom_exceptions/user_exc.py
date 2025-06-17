import uuid

from rest_framework import status

from core.apps.common.exceptions.base_exception import ServiceException


class UserNotFoundException(ServiceException):
    """Исключение: Пользователь не найден."""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Пользователь не найден."

    def __init__(self, user_id: uuid.UUID = None):
        detail = self.default_detail
        if user_id:
            # Детализация сообщения, если передан user_id
            detail = f"Пользователь с ID '{user_id}' не найден."
        super().__init__(detail=detail, code="user_not_found")


class ValidationErrorAPI(ServiceException):
    """Исключение: Ошибка валидации данных API."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Ошибка валидации."
    default_code = "validation_error"

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        # Если детализация не является словарем (например, это строка),
        # оборачиваем её в словарь для совместимости с форматом ошибок DRF
        if not isinstance(detail, dict):
            detail = {"non_field_errors": [detail]}
        super().__init__(detail=detail, code=code)


class UserEmailNotFoundException(ServiceException):
    """Исключение: Пользователь с указанным email не найден."""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Пользователь не найден."

    def __init__(self, user_email: str):
        detail = self.default_detail
        # Уточнение: здесь в сообщении должно быть user_email, а не user_id
        if user_email:
            detail = f"Пользователь с email '{user_email}' не найден."
        super().__init__(detail=detail, code="user_not_found")


class UserCreationError(ServiceException):
    """Исключение: Произошла ошибка при создании пользователя."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Произошла ошибка при создании пользователя."

    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail or self.default_detail, code=code)


class EmptyUpdateDataError(ServiceException):
    """Исключение: Нет данных для обновления пользователя."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Нет данных для обновления."

    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail or self.default_detail, code=code)


class UserDeleteError(ServiceException):
    """Исключение: Произошла ошибка при удалении пользователя."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Произошла ошибка при удалении пользователя."

    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail or self.default_detail, code=code)


class UserActiveDeleteError(ServiceException):
    """Исключение: Попытка удаления активного пользователя."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Пользователь активен. Невозможно удалить."

    def __init__(self, user_id: uuid.UUID):
        # Здесь была ошибка: self.detail и self.code могут быть не определены,
        # если не переданы в super(). Лучше использовать default_detail/code.
        super().__init__(detail=self.default_detail, code="user_active_delete_error")


class UserUpdateError(ServiceException):
    """Исключение: Произошла ошибка при обновлении пользователя."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Произошла ошибка при обновлении пользователя."

    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail or self.default_detail, code=code)


class UserExistsError(Exception):
    """Исключение: Пользователь уже существует или его данные конфликтуют."""

    def __init__(self, message="Пользователь уже существует или ID Telegram конфликтует.", phone=None):
        super().__init__(message)
        self.phone = phone
        if phone:
            # Детализация сообщения, если передан номер телефона
            self.message = f"Пользователь с номером телефона '{phone}' уже привязан к другому аккаунту Telegram."
        else:
            self.message = message

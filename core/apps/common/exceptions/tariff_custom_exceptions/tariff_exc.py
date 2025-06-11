import uuid

from rest_framework import status

from core.apps.common.exceptions.base_exception import ServiceException


class TariffNotFoundException(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Тариф не найден."

    def __init__(self, tariff_id: uuid.UUID = None):
        detail = self.default_detail
        if tariff_id:
            detail = f"Тариф с ID '{tariff_id}' не найден."
        super().__init__(detail=detail, code="user_not_found")


class TariffCreationError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Произошла ошибка при создании тарифа."

    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail or self.default_detail, code=code)


class EmptyTariffDataError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Нет данных для обновления."

    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail or self.default_detail, code=code)


class TariffDeleteError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Произошла ошибка при удалении тарифа."

    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail or self.default_detail, code=code)


class TariffActiveDeleteError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Тариф активен."

    def __init__(self, tariff_id: uuid.UUID):
        super().__init__(detail=self.detail or self.default_detail, code=self.code)


class TariffUpdateException(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Произошла ошибка при обновлении тарифа."

    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail or self.default_detail, code=code)

import uuid
from core.apps.common.exceptions.base_exception import ServiceException
from rest_framework import status


class SubscriptionCreationError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Произошла ошибка при создании подписик."

    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail or self.default_detail, code=code)


class SubscriptionNotFoundException(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Подписка не найден."

    def __init__(self, sub_id: str):
        detail = self.default_detail
        if sub_id:
            detail = f"Подписка с ID '{sub_id}' не найден."
        super().__init__(detail=detail, code="user_not_found")


class SubscriptionUpdateError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Произошла ошибка при обновлении подписки."

    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail or self.default_detail, code=code)


class SubscriptionDeleteError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Произошла ошибка при удалении тарифа."

    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail or self.default_detail, code=code)


class SubscriptionActiveDeleteError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Тариф активен."

    def __init__(self, tariff_id: uuid.UUID):
        super().__init__(detail=self.detail or self.default_detail, code=self.code)

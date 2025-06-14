from core.apps.common.exceptions.base_exception import ServiceException
from rest_framework import status


class OrderCreationError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Произошла ошибка при создании заказа."

    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail or self.default_detail, code=code)


class OrderNotFoundException(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Заказ не найден."

    def __init__(self, order_id: str):
        detail = self.default_detail
        if order_id:
            detail = f"Заказ с ID '{order_id}' не найден."
        super().__init__(detail=detail, code="user_not_found")


class OrderUpdateError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Произошла ошибка при обновлении заказа."

    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail or self.default_detail, code=code)


class OrderDeleteError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Произошла ошибка при удалении заказа."

    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail or self.default_detail, code=code)


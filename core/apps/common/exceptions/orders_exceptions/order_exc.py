from core.apps.common.exceptions.base_exception import ServiceException
from rest_framework import status


class OrderCreationError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Произошла ошибка при создании заказа."

    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail or self.default_detail, code=code)

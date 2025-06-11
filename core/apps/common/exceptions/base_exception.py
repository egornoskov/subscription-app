from typing import Any

from rest_framework import status
from rest_framework.exceptions import APIException


class ServiceException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "An unexpected service error occurred"
    default_code = "service_error"

    def __init__(self, detail: Any = None, code: str = None):
        if detail is not None:
            self.detail = detail
        if code is not None:
            self.code = code
        super().__init__(detail, code)

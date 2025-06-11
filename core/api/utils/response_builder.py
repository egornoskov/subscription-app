# core/api/utils.py

from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from rest_framework import status
from rest_framework.response import Response

from core.api.schemas.response_schemas import ApiResponse


def build_api_response(
    data: Optional[Any] = None,
    message: str = "OK",
    meta: Optional[Dict[str, Any]] = None,
    errors: Optional[List[Any]] = None,
    status_code: int = status.HTTP_200_OK,
) -> Response:
    """
    Строит стандартизированный API-ответ на основе Pydantic-схемы ApiResponse.
    """
    if meta is None:
        meta = {}
    if errors is None:
        errors = []

    api_response_payload = ApiResponse(
        message=message,
        data=data,
        meta=meta,
        errors=errors,
    )
    return Response(api_response_payload.model_dump(exclude_none=True), status=status_code)

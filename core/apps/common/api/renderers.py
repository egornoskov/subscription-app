from typing import (
    Any,
    Dict,
    Optional,
)

from rest_framework.renderers import JSONRenderer
from rest_framework.status import is_success
from rest_framework.utils.serializer_helpers import (
    ReturnDict,
    ReturnList,
)

from core.api.schemas.response_schemas import ApiResponse


class CustomAPIRenderer(JSONRenderer):
    media_type = "application/json"
    format = "json"
    charset = "utf-8"

    def render(
        self, data: Any, accepted_media_type: Optional[str] = None, renderer_context: Optional[Dict[str, Any]] = None
    ) -> bytes:
        response = renderer_context.get("response")

        if response and not is_success(response.status_code) and not isinstance(data, dict):
            return super().render(data, accepted_media_type, renderer_context)

        if isinstance(data, dict) and all(key in data for key in ["message", "data", "meta", "errors"]):
            final_data_to_render = data
        elif isinstance(data, (dict, list, ReturnDict, ReturnList)):
            final_data_to_render = ApiResponse(data=data).model_dump(exclude_none=True)
        else:
            final_data_to_render = ApiResponse(data=data).model_dump(exclude_none=True)

        return super().render(final_data_to_render, accepted_media_type, renderer_context)

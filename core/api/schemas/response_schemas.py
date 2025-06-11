from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    TypeVar,
)

from pydantic import (
    BaseModel,
    Field,
)

from core.api.schemas.pagination import PaginationOut


TData = TypeVar("TData")
TListItem = TypeVar("TListItem")


class ListResponsePayload(BaseModel, Generic[TListItem]):
    """
    Представляет структуру 'data' для пагинированного списка в итоговом ответе.
    """

    items: List[TData] = None
    pagination: PaginationOut


class ApiResponse(BaseModel, Generic[TData]):
    """
    Основная Pydantic-схема для всей структуры API-ответа.
    Это то, что вы будете возвращать из View.
    """

    message: str = "OK"
    data: Optional[TListItem] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
    errors: List[Any] = Field(default_factory=list)

    class Config:

        extra = "allow"

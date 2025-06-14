import uuid
from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Iterable,
)

from core.api.schemas.pagination import PaginationIn
from core.api.v1.products.schemas.filters import OrderFilter
from core.apps.products.models import Order


class OrderBaseService(ABC):

    @abstractmethod
    def create_order(
        self,
        user_id: uuid.UUID,
        product_id: uuid.UUID,
        description: str | None = None,
    ) -> Order:
        pass

    # @abstractmethod
    # def get_order_by_id(self, order_id: uuid.UUID) -> Optional[Order]:
    #     pass

    # @abstractmethod
    # def soft_delete_order(self, order_id: uuid.UUID) -> Order:
    #     pass

    # @abstractmethod
    # def hard_delete_order(self, order_id: uuid.UUID) -> None:
    #     pass

    @abstractmethod
    def get_order_list(
        self,
        filters: OrderFilter,
        pagination_in: PaginationIn,
        user_id: uuid.UUID | None = None,
        is_admin: bool = False,
    ) -> Iterable[Order]:
        pass

    @abstractmethod
    def get_order_count(
        self,
        filters: OrderFilter,
        user_id: uuid.UUID | None = None,
        is_admin: bool = False,
    ) -> int:
        pass

    # @abstractmethod
    # def get_order_list_archive(
    #     self, filters: OrderFilter, pagination_in: PaginationIn
    # ) -> Iterable[Order]:
    #     pass

    # @abstractmethod
    # def get_order_count_archive(self, filters: OrderFilter) -> int:
    #     pass

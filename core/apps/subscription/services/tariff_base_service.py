from decimal import Decimal
import uuid
from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Iterable,
    Iterator,
    Optional,
)

from core.api.schemas.pagination import PaginationIn
from core.api.v1.subscriptions.schemas.filters import TariffFilter
from core.apps.subscription.models import Tariff


class TariffBaseService(ABC):

    # @abstractmethod
    # def create_tariff(
    #     self,
    #     id: uuid.UUID,
    #     name: str,
    #     price: Decimal,
    # ) -> "Tariff":
    #     pass

    # @abstractmethod
    # def get_tariff_by_id(self, tariff_uuid: uuid.UUID) -> Optional[Tariff]:
    #     pass

    # @abstractmethod
    # def soft_delete_tariff(self, tariff_uuid: uuid.UUID) -> Tariff:
    #     pass

    # @abstractmethod
    # def hard_delete_tariff(self, tariff_uuid: uuid.UUID) -> None:
    #     pass

    @abstractmethod
    def get_tariff_list(self, filters: TariffFilter, pagination_in: PaginationIn) -> Iterator[Tariff]:
        pass

    @abstractmethod
    def get_tariff_count(self, filters: TariffFilter) -> int:
        pass

    # @abstractmethod
    # def get_all_tariff_archive(self, filters: TariffFilter, pagination_in: PaginationIn) -> Iterable[Tariff]:
    #     pass

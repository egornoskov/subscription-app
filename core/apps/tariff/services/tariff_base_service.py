import uuid
from abc import (
    ABC,
    abstractmethod,
)
from decimal import Decimal
from typing import (  # Iterable,
    Iterable,
    Iterator,
    Optional,
)

from core.api.schemas.pagination import PaginationIn
from core.api.v1.tariff.schemas.filters import TariffFilter
from core.apps.tariff.models import Tariff


class TariffBaseService(ABC):

    @abstractmethod
    def create_tariff(
        self,
        name: str,
        price: Decimal,
    ) -> "Tariff":
        pass

    @abstractmethod
    def get_tariff_by_id(self, tariff_uuid: uuid.UUID) -> Optional[Tariff]:
        pass

    @abstractmethod
    def soft_delete_tariff(self, tariff_uuid: uuid.UUID) -> Tariff:
        pass

    # @abstractmethod
    # def hard_delete_tariff(self, tariff_uuid: uuid.UUID) -> None:
    #     pass

    @abstractmethod
    def get_tariff_list(self, filters: TariffFilter, pagination_in: PaginationIn) -> Iterator[Tariff]:
        pass

    @abstractmethod
    def get_tariff_count(self, filters: TariffFilter) -> int:
        pass

    @abstractmethod
    def get_tariff_list_archive(self, filters: TariffFilter, pagination_in: PaginationIn) -> Iterable[Tariff]:
        pass

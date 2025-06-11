from typing import (
    Iterator,
)
from django.db.models import Q
from core.api.schemas.pagination import PaginationIn
from core.api.v1.subscriptions.schemas.filters import TariffFilter
from core.apps.subscription.models import Tariff
from core.apps.subscription.services.tariff_base_service import TariffBaseService


class TariffService(TariffBaseService):
    def _build_tariff_query(self, filters: TariffFilter | None = None) -> Q:
        query = Q()

        if filters and filters.search is not None:
            query &= Q(name__icontains=filters.search)
        return query

    def get_tariff_list(self, filters: TariffFilter, pagination_in: PaginationIn) -> Iterator[Tariff]:
        query = self._build_tariff_query(filters)
        queryset = Tariff.objects.filter(query)
        tariffs = queryset[pagination_in.offset : pagination_in.offset + pagination_in.limit]
        return tariffs

    def get_tariff_count(self, filters: TariffFilter) -> int:
        query = self._build_tariff_query(filters)
        return Tariff.objects.filter(query).count()

    # def create_tariff(
    #     self,
    #     id: uuid.UUID,
    #     name: str,
    #     price: Decimal,
    # ) -> "Tariff":
    #     pass

    # def get_tariff_by_id(self, tariff_uuid: uuid.UUID) -> Optional[Tariff]:
    #     pass

    # def soft_delete_tariff(self, tariff_uuid: uuid.UUID) -> Tariff:
    #     pass

    # def hard_delete_tariff(self, tariff_uuid: uuid.UUID) -> None:
    #     pass


# def get_all_tariff_archive(self, filters: TariffFilter, pagination_in: PaginationIn) -> Iterable[Tariff]:
#     pass

import uuid
from decimal import Decimal
from typing import (
    Iterator,
    Optional,
)

from django.db.models import Q
from psycopg2 import IntegrityError

from core.api.schemas.pagination import PaginationIn
from core.api.v1.tariff.schemas.filters import TariffFilter
from core.api.v1.tariff.schemas.schemas import TariffUpdateSchema
from core.apps.common.exceptions.tariff_custom_exceptions.tariff_exc import (
    EmptyTariffDataError,
    TariffCreationError,
    TariffNotFoundException,
    TariffUpdateException,
)
from core.apps.tariff.models import Tariff
from core.apps.tariff.services.tariff_base_service import TariffBaseService


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

    def create_tariff(
        self,
        name: str,
        price: Decimal,
    ) -> Tariff:
        try:
            tariff = Tariff.objects.create(
                name=name,
                price=price,
            )
            return tariff
        except IntegrityError as e:
            raise TariffCreationError(detail=f"Ошибка базы данных при создании тарифа: {e}")
        except Exception as e:
            raise TariffCreationError(detail=f"Неизвестная ошибка при создании тарифа: {e}")

    def get_tariff_by_id(self, tariff_uuid: uuid.UUID) -> Optional[Tariff]:

        tariff = Tariff.objects.get_or_none(id=tariff_uuid)

        if tariff is None:
            raise TariffNotFoundException(tariff_id=tariff_uuid)
        return tariff

    def update_tariff(self, tariff_uuid: uuid.UUID, data_to_update: TariffUpdateSchema) -> Tariff:
        try:
            tariff = self.get_tariff_by_id(tariff_uuid=tariff_uuid)
            tariff.name = data_to_update.name
            tariff.price = data_to_update.price

            tariff.full_clean()
            tariff.save()

            return tariff
        except IntegrityError as e:
            raise TariffUpdateException(detail=f"Ошибка базы данных при полном обновлении тарифа: {e}")
        except Exception as e:
            raise TariffUpdateException(detail=f"Неизвестная ошибка при полном обновлении тарифа: {e}")

    def partial_update_tariff(self, tariff_uuid: uuid.UUID, data_to_update: TariffUpdateSchema) -> Tariff:
        updated_data = data_to_update.model_dump(exclude_unset=True)

        if not updated_data:
            raise EmptyTariffDataError()

        try:
            tariff = self.get_tariff_by_id(tariff_uuid=tariff_uuid)
            for key, value in updated_data.items():
                setattr(tariff, key, value)

            tariff.full_clean()
            tariff.save()

            return tariff
        except IntegrityError as e:
            raise TariffUpdateException(detail=f"Ошибка базы данных при частичном обновлении тарифа: {e}")
        except Exception as e:
            raise TariffUpdateException(detail=f"Неизвестная ошибка при частичном обновлении тарифа: {e}")

    # def soft_delete_tariff(self, tariff_uuid: uuid.UUID) -> Tariff:
    #     pass

    # def hard_delete_tariff(self, tariff_uuid: uuid.UUID) -> None:
    #     pass

    # def get_all_tariff_archive(self, filters: TariffFilter, pagination_in: PaginationIn) -> Iterable[Tariff]:
    #     pass

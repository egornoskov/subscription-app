import uuid
from decimal import Decimal
from typing import (
    Iterable,
    Iterator,
)

from django.db.models import Q
from django.utils import timezone
from psycopg2 import IntegrityError

from core.api.schemas.pagination import PaginationIn
from core.api.v1.tariff.schemas.filters import TariffFilter
from core.api.v1.tariff.schemas.schemas import TariffUpdateSchema
from core.apps.common.exceptions.base_exception import ServiceException
from core.apps.common.exceptions.tariff_custom_exceptions.tariff_exc import (
    EmptyTariffDataError,
    TariffActiveDeleteError,
    TariffCreationError,
    TariffDeleteError,
    TariffNotFoundError,
    TariffUpdateError,
)
from django.db import transaction
from core.apps.tariff.models import Tariff
from core.apps.tariff.services.tariff_base_service import TariffBaseService


class TariffService(TariffBaseService):
    def _build_tariff_query(self, filters: TariffFilter | None = None) -> Q:
        """Строит объект Q для фильтрации тарифов на основе заданных фильтров.

        Args:
            filters (TariffFilter | None): Объект с параметрами фильтрации тарифов.

        Returns:
            Q: Объект Q для использования в запросах Django ORM.
        """
        query = Q()

        if filters and filters.search is not None:
            query &= Q(name__icontains=filters.search)
        return query

    def get_tariff_list(self, filters: TariffFilter, pagination_in: PaginationIn) -> Iterator[Tariff]:
        """Получает список активных тарифов.

        Фильтрует по заданным критериям и применяет пагинацию.

        Args:
            filters (TariffFilter): Объект с параметрами фильтрации тарифов.
            pagination_in (PaginationIn): Объект с параметрами пагинации (offset, limit).

        Returns:
            Iterator[Tariff]: Итерируемый объект активных тарифов.
        """
        query = self._build_tariff_query(filters)
        queryset = Tariff.objects.filter(query)
        tariffs = queryset[pagination_in.offset : pagination_in.offset + pagination_in.limit]
        return tariffs

    def get_tariff_count(self, filters: TariffFilter) -> int:
        """Получает общее количество активных тарифов.

        Подсчитывает количество тарифов с учетом заданных фильтров.

        Args:
            filters (TariffFilter): Объект с параметрами фильтрации тарифов.

        Returns:
            int: Общее количество активных тарифов.
        """
        query = self._build_tariff_query(filters)
        return Tariff.objects.filter(query).count()

    def get_tariff_by_id(self, tariff_uuid: uuid.UUID) -> Tariff:
        """Получает тариф по его UUID.

        Args:
            tariff_uuid (uuid.UUID): UUID тарифа.

        Raises:
            TariffNotFoundError: Если тариф с указанным UUID не найден.

        Returns:
            Tariff: Найденный объект тарифа.
        """
        tariff = Tariff.objects.get_or_none(id=tariff_uuid)

        if tariff is None:
            raise TariffNotFoundError(tariff_id=tariff_uuid)
        return tariff

    def get_tariff_list_archive(self, filters: TariffFilter, pagination_in: PaginationIn) -> Iterable[Tariff]:
        """Получает список архивированных (мягко удаленных) тарифов.

        Фильтрует по заданным критериям и применяет пагинацию.

        Args:
            filters (TariffFilter): Объект с параметрами фильтрации тарифов.
            pagination_in (PaginationIn): Объект с параметрами пагинации (offset, limit).

        Returns:
            Iterable[Tariff]: Итерируемый объект архивированных тарифов.
        """
        query = self._build_tariff_query(filters)
        queryset = Tariff.objects.unfiltered().filter(
            query,
            is_deleted=True,
        )
        tariffs = queryset[pagination_in.offset : pagination_in.offset + pagination_in.limit]
        return tariffs

    def get_tariffs_count_archive(self, filters: TariffFilter) -> int:
        """Получает общее количество архивированных (мягко удаленных) тарифов.

        Подсчитывает количество тарифов с учетом заданных фильтров.

        Args:
            filters (TariffFilter): Объект с параметрами фильтрации тарифов.

        Returns:
            int: Общее количество архивированных тарифов.
        """
        query = self._build_tariff_query(filters)
        return Tariff.objects.unfiltered().filter(query, is_deleted=True).count()

    def create_tariff(
        self,
        name: str,
        price: Decimal,
    ) -> Tariff:
        """Создает новый тариф.

        Args:
            name (str): Название тарифа.
            price (Decimal): Цена тарифа.

        Raises:
            TariffCreationError: Если произошла ошибка при создании тарифа.

        Returns:
            Tariff: Созданный объект тарифа.
        """
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

    @transaction.atomic
    def update_tariff(self, tariff_uuid: uuid.UUID, data_to_update: TariffUpdateSchema) -> Tariff:
        """Полностью обновляет существующий тариф по его UUID.

        Обновляет все поля тарифа, используя предоставленные данные.

        Args:
            tariff_uuid (uuid.UUID): UUID тарифа для обновления.
            data_to_update (TariffUpdateSchema): Схема с новыми данными для тарифа.

        Raises:
            TariffNotFoundError: Если тариф с указанным UUID не найден.
            TariffUpdateError: Если произошла ошибка при обновлении тарифа.

        Returns:
            Tariff: Обновленный объект тарифа.
        """
        try:
            tariff = self.get_tariff_by_id(tariff_uuid=tariff_uuid)
            tariff.name = data_to_update.name
            tariff.price = data_to_update.price

            tariff.full_clean()
            tariff.save()

            return tariff
        except IntegrityError as e:
            raise TariffUpdateError(detail=f"Ошибка базы данных при полном обновлении тарифа: {e}")
        except Exception as e:
            raise TariffUpdateError(detail=f"Неизвестная ошибка при полном обновлении тарифа: {e}")

    @transaction.atomic
    def partial_update_tariff(self, tariff_uuid: uuid.UUID, data_to_update: TariffUpdateSchema) -> Tariff:
        """Частично обновляет существующий тариф по его UUID.

        Обновляет только те поля тарифа, которые указаны в `data_to_update`.

        Args:
            tariff_uuid (uuid.UUID): UUID тарифа для частичного обновления.
            data_to_update (TariffUpdateSchema): Схема с данными для частичного обновления.

        Raises:
            EmptyTariffDataError: Если в `data_to_update` нет данных для обновления.
            TariffNotFoundError: Если тариф с указанным UUID не найден.
            TariffUpdateError: Если произошла ошибка при обновлении тарифа.

        Returns:
            Tariff: Частично обновленный объект тарифа.
        """
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
            raise TariffUpdateError(detail=f"Ошибка базы данных при частичном обновлении тарифа: {e}")
        except Exception as e:
            raise TariffUpdateError(detail=f"Неизвестная ошибка при частичном обновлении тарифа: {e}")

    @transaction.atomic
    def soft_delete_tariff(self, tariff_uuid: uuid.UUID) -> Tariff:
        """Мягко удаляет тариф по его UUID.

        Устанавливает флаг `is_deleted` в True и `deleted_at` в текущее время.

        Args:
            tariff_uuid (uuid.UUID): UUID тарифа для мягкого удаления.

        Raises:
            TariffNotFoundError: Если тариф с указанным UUID не найден.
            TariffDeleteError: Если произошла ошибка при мягком удалении тарифа.

        Returns:
            Tariff: Объект тарифа после мягкого удаления.
        """
        try:
            tariff = self.get_tariff_by_id(tariff_uuid=tariff_uuid)

            tariff.is_deleted = True
            tariff.deleted_at = timezone.now()

            tariff.full_clean()
            tariff.save()
            return tariff
        except IntegrityError as e:
            raise TariffDeleteError(detail=f"Ошибка базы данных при мягком удалении тарифа: {e}")
        except Exception as e:
            raise TariffDeleteError(detail=f"Неизвестная ошибка при мягком удалении тарифа: {e}")

    def hard_delete_tariff(self, tariff_uuid: uuid.UUID) -> None:
        try:
            query = self._build_tariff_query()
            tariff = Tariff.objects.unfiltered().filter(id=tariff_uuid).filter(query).first()

            if not tariff:
                raise TariffNotFoundError(user_id=tariff_uuid)

            if tariff.is_deleted is False:
                raise TariffActiveDeleteError(tariff_id=tariff_uuid)

            tariff.hard_delete()
            return None
        except ServiceException as e:
            raise e
        except Exception as e:
            raise TariffDeleteError(detail=f"Неизвестная ошибка при полном удалении пользователя: {e}")

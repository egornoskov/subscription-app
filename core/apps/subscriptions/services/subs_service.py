import datetime
import uuid
from typing import (
    Iterable,
    Optional,
)

from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from psycopg2 import IntegrityError

from core.api.schemas.pagination import PaginationIn
from core.api.v1.subscriptions.schemas.filters import SubscriptionFilter
from core.apps.common.exceptions.subs_exception.subs_exc import (
    SubscriptionCreationError,
    SubscriptionDeleteError,
    SubscriptionNotFoundException,
    SubscriptionUpdateError,
)
from core.apps.subscriptions.models import Subscription
from core.apps.subscriptions.services.base_service import SubscriptionBaseService
from core.apps.tariff.models import Tariff


class SubscriptionService(SubscriptionBaseService):

    def _build_query_subs(
        self,
        filters: SubscriptionFilter | None = None,
        user_id: uuid.UUID | None = None,
        is_admin: bool = False,
    ) -> Q:
        query = Q()

        if user_id and not is_admin:
            query &= Q(user_id=user_id)

        if filters and filters.search is not None:
            query &= Q(tariff__name__icontains=filters.search)
        return query

    def get_subscription_list(
        self,
        filters: SubscriptionFilter,
        pagination_in: PaginationIn,
        user_id: uuid.UUID | None = None,
        is_admin: bool = False,
    ) -> Iterable[Subscription]:
        query = self._build_query_subs(filters, user_id, is_admin)

        if is_admin:
            queryset = Subscription.objects.filter(query).select_related("user", "tariff")
        else:
            queryset = Subscription.objects.filter(query).select_related("tariff")

        subscriptions = queryset[pagination_in.offset : pagination_in.offset + pagination_in.limit]

        return subscriptions

    def get_subscription_count(
        self,
        filters: SubscriptionFilter,
        user_id: uuid.UUID | None = None,
        is_admin: bool = False,
    ) -> int:
        query = self._build_query_subs(filters, user_id, is_admin)
        return Subscription.objects.filter(query).count()

    def create_subscription(
        self,
        user_id: uuid.UUID,
        tariff_id: uuid.UUID,
        month_duration: int,
    ) -> Subscription:
        try:
            current_datetime = timezone.now()
            end_datetime = current_datetime + relativedelta(months=month_duration)

            subscription = Subscription.objects.create(
                user_id=user_id,
                tariff_id=tariff_id,
                start_date=current_datetime,
                end_date=end_datetime,
                is_active=True,
            )
            return subscription
        except IntegrityError as e:
            error_message = str(e)
            if "violates foreign key constraint" in error_message:
                if "user_id" in error_message:
                    raise SubscriptionCreationError(detail=f"Пользователь с ID {user_id} не найден.")
                elif "tariff_id" in error_message:
                    raise SubscriptionCreationError(detail=f"Тариф с ID {tariff_id} не найден.")
                else:
                    raise SubscriptionCreationError(
                        detail=f"Ошибка внешнего ключа при создании подписки: {error_message}"
                    )
            elif "duplicate key value violates unique constraint" in error_message:
                raise SubscriptionCreationError(
                    detail="Подписка с таким пользователем, тарифом и датой начала уже существует."
                )
            else:
                raise SubscriptionCreationError(
                    detail=f"Ошибка целостности данных при создании подписки: {error_message}"
                )
        except Exception as e:
            raise SubscriptionCreationError(detail=f"Непредвиденная ошибка при создании подписки: {str(e)}")

    def get_subscription_by_id(
        self,
        sub_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> Optional[Subscription]:

        query = self._build_query_subs(user_id=user_id)

        subscription = Subscription.objects.filter(id=sub_id).filter(query).first()

        if subscription is None:
            raise SubscriptionNotFoundException(sub_id=sub_id)

        return subscription

    @transaction.atomic
    def update_subscription(self, sub_uuid: uuid.UUID, tariff: Tariff, end_date: datetime.date) -> Subscription:
        try:
            sub = self.get_subscription_by_id(sub_uuid)

            sub.tariff = tariff
            sub.end_date = end_date

            sub.full_clean()
            sub.save()
            return sub

        except IntegrityError as e:
            raise SubscriptionUpdateError(detail=f"Ошибка базы данных при полном обновлении тарифа: {e}")
        except Exception as e:
            raise SubscriptionUpdateError(detail=f"Неизвестная ошибка при полном обновлении тарифа: {e}")

    @transaction.atomic
    def partial_update_subscription(
        self,
        sub_uuid: uuid.UUID,
        tariff: Optional[Tariff] = None,
        end_date: Optional[datetime.date] = None,
    ) -> Subscription:
        subscription = self.get_subscription_by_id(sub_uuid)

        try:
            if tariff is not None:
                subscription.tariff = tariff
            if end_date is not None:
                subscription.end_date = end_date

            subscription.full_clean()
            subscription.save()
            return subscription

        except IntegrityError as e:
            raise SubscriptionUpdateError(detail=f"Ошибка базы данных при полном обновлении тарифа: {e}")
        except Exception as e:
            raise SubscriptionUpdateError(detail=f"Неизвестная ошибка при полном обновлении тарифа: {e}")

    @transaction.atomic
    def soft_delete_subscription(self, sub_id: uuid.UUID) -> Subscription:
        try:
            subscritpion: Subscription = self.get_subscription_by_id(sub_id=sub_id)

            subscritpion.is_deleted = True
            subscritpion.is_active = False
            subscritpion.deleted_at = timezone.now()

            subscritpion.full_clean()
            subscritpion.save()
            return subscritpion
        except IntegrityError as e:
            raise SubscriptionDeleteError(detail=f"Ошибка базы данных при мягком удалении тарифа: {e}")
        except Exception as e:
            raise SubscriptionDeleteError(detail=f"Неизвестная ошибка при мягком удалении тарифа: {e}")

    def hard_delete_subscription(self, sub_id: uuid.UUID) -> Subscription:
        try:
            subscription = self.get_subscription_by_id(sub_id=sub_id)

            subscription.delete()
            return subscription
        except Exception as e:
            raise SubscriptionDeleteError(detail=f"Неизвестная ошибка при мягком удалении тарифа: {e}")

    def get_subscription_list_archive(
        self, filters: SubscriptionFilter, pagination_in: PaginationIn
    ) -> Iterable[Subscription]:
        query = self._build_user_query(filters)
        queryset = Subscription.objects.unfiltered().filter(
            query,
            is_deleted=True,
            is_active=False,
        )
        combined_query = queryset.select_related("user", "tariff")

        subscriptions = combined_query[pagination_in.offset : pagination_in.offset + pagination_in.limit]

        return subscriptions

    def get_subscription_count_archive(self, filters: SubscriptionFilter) -> int:
        query = self._build_user_query(filters)
        return (
            Subscription.objects.unfiltered()
            .filter(
                query,
                is_deleted=True,
                is_active=False,
            )
            .count()
        )

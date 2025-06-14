import uuid
from typing import (
    Iterable,
    Optional,
)

from django.db.models import Q
from django.db import IntegrityError

from core.api.schemas.pagination import PaginationIn
from core.api.v1.products.schemas.filters import OrderFilter
from core.apps.products.models import Order
from core.apps.products.services.base_order_service import OrderBaseService
from django.db import transaction

from core.apps.common.exceptions.orders_exceptions.order_exc import (
    OrderCreationError,
    OrderDeleteError,
    OrderNotFoundException,
    OrderUpdateError,
)


class OrderService(OrderBaseService):
    def _build_query_orders(
        self,
        filters: OrderFilter | None = None,
        user_id: uuid.UUID | None = None,
        is_admin: bool = False,
    ) -> Q:
        query = Q(is_deleted=False)

        if user_id and not is_admin:
            query &= Q(user_id=user_id)

        if filters and filters.search is not None:
            query &= Q(description__icontains=filters.search) | Q(product__title__icontains=filters.search)
        return query

    def create_order(
        self,
        user_id: uuid.UUID,
        product_id: uuid.UUID,
        description: str | None = None,
    ) -> Order:
        try:
            order = Order.objects.create(
                user_id=user_id,
                product_id=product_id,
                description=description,
            )
            return order
        except IntegrityError as e:
            raise OrderCreationError(detail=f"Ошибка базы данных при создании заказа: {e}")
        except Exception as e:
            raise OrderCreationError(detail=f"Непредвиденная ошибка при создании заказа: {str(e)}")

    def get_order_list(
        self,
        filters: OrderFilter,
        pagination_in: PaginationIn,
        user_id: uuid.UUID | None = None,
        is_admin: bool = False,
    ) -> Iterable[Order]:
        query = self._build_query_orders(filters, user_id, is_admin)

        if is_admin:
            queryset = Order.objects.filter(query).select_related("product", "user")
        else:

            queryset = Order.objects.filter(query).select_related("product")

        orders = queryset[pagination_in.offset : pagination_in.offset + pagination_in.limit]
        return orders

    def get_order_count(
        self,
        filters: OrderFilter,
        user_id: uuid.UUID | None = None,
        is_admin: bool = False,
    ) -> int:
        query = self._build_query_orders(filters, user_id, is_admin)
        return Order.objects.filter(query).count()

        # def get_order_by_id(self, order_id: uuid.UUID) -> Optional[Order]:
        #     raise NotImplementedError("Метод get_order_by_id не реализован")

        # def soft_delete_order(self, order_id: uuid.UUID) -> Order:
        #     raise NotImplementedError("Метод soft_delete_order не реализован")

    def get_order_by_id(
        self,
        order_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> Optional[Order]:

        query = self._build_query_orders(user_id=user_id)

        final_query = query & Q(id=order_id)

        order = Order.objects.filter(final_query).first()

        if order is None:
            raise OrderNotFoundException(order_id=order_id)

        return order

    @transaction.atomic
    def update_order(self, order_id: uuid.UUID, data: dict) -> Order:
        try:
            order = self.get_order_by_id(order_id=order_id)

            if "description" in data:
                order.description = data["description"]

            order.full_clean()
            order.save()
            return order

        except IntegrityError as e:
            raise OrderUpdateError(detail=f"Ошибка базы данных при полном обновлении заказа: {e}")
        except Exception as e:
            raise OrderUpdateError(detail=f"Неизвестная ошибка при полном обновлении заказа: {e}")

    @transaction.atomic
    def soft_delete_order(self, order_id: uuid.UUID) -> Order:
        try:
            order: Order = self.get_order_by_id(order_id=order_id)

            order.is_deleted = True

            order.full_clean()
            order.save()
            return order
        except IntegrityError as e:
            raise OrderDeleteError(detail=f"Ошибка базы данных при мягком удалении заказа: {e}")
        except Exception as e:
            raise OrderDeleteError(detail=f"Неизвестная ошибка при мягком удалении заказа: {e}")

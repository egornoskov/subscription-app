import uuid
from abc import (
    ABC,
    abstractmethod,
)
from typing import (  # Iterable,
    Iterable,
    Optional,
)

from core.api.schemas.pagination import PaginationIn
from core.api.v1.subscriptions.schemas.filters import SubscriptionFilter
from core.apps.subscriptions.models import Subscription


class SubscriptionBaseService(ABC):

    @abstractmethod
    def create_subscription(
        self,
        user_id: uuid.UUID,
        tariff_id: uuid.UUID,
        month_duration: int,
    ) -> Subscription:
        pass

    @abstractmethod
    def get_subscription_by_id(self, sub_id: uuid.UUID) -> Optional[Subscription]:
        pass

    @abstractmethod
    def soft_delete_subscription(self, sub_id: uuid.UUID) -> Subscription:
        pass

    # @abstractmethod
    # def hard_delete_tariff(self, tariff_uuid: uuid.UUID) -> None:
    #     pass

    @abstractmethod
    def get_subscription_list(self, filters: SubscriptionFilter, pagination_in: PaginationIn) -> Iterable[Subscription]:
        pass

    @abstractmethod
    def get_subscription_count(self, filters: SubscriptionFilter) -> int:
        pass

    # @abstractmethod
    # def get_subscription_list_archive(
    #     self, filters: SubscriptionFilter, pagination_in: PaginationIn
    # ) -> Iterable[Subscription]:
    #     pass

    # @abstractmethod
    # def get_subscription_count_archive(self, filters: SubscriptionFilter) -> int:
    #     pass

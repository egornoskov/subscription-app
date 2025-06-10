import uuid
from typing import Iterable

from django.db.models import Q

from core.api.pagination import PaginationIn
from core.api.v1.users.filters import UserFilter
from core.apps.common.exceptions.user_custom_exceptions.user_exc import (
    UserEmailNotFoundException,
    UserNotFoundException,
)
from core.apps.user.models import User
from core.apps.user.services.base_user_service import BaseUserService


class UserService(BaseUserService):
    def _build_user_query(self, filters: UserFilter | None = None) -> Q:
        query = Q(is_superuser=False)

        if filters.search is not None and filters is not None:
            query &= (
                Q(first_name__icontains=filters.search)
                | Q(last_name__icontains=filters.search)
                | Q(email__icontains=filters.search)
            )
        return query

    def get_all_users_unfiltered(self, filters: UserFilter, pagination_in: PaginationIn) -> Iterable[User]:
        query = self._build_user_query(filters)
        queryset = User.objects.unfiltered().filter(query)
        queryset = queryset.prefetch_related("user_subscription__tariff")
        users = queryset[pagination_in.offset : pagination_in.offset + pagination_in.limit]
        return users

    def get_users_count_unfiltered(self, filters: UserFilter) -> int:
        query = self._build_user_query(filters)
        return User.objects.unfiltered().filter(query).count()

    def get_users_list(self, filters: UserFilter, pagination_in: PaginationIn) -> Iterable[User]:
        query = self._build_user_query(filters)
        queryset = User.objects.filter(query)
        queryset = queryset.prefetch_related("user_subscription__tariff")
        users = queryset[pagination_in.offset : pagination_in.offset + pagination_in.limit]
        return users

    def get_users_count(self, filters: UserFilter) -> int:
        query = self._build_user_query(filters)
        return User.objects.filter(query).count()

    def get_user_by_id(self, user_id: uuid.UUID) -> User:
        query = self._build_user_query()
        user = User.objects.filter(id=user_id).filter(query).first()

        if user is None:
            raise UserNotFoundException(user_id=user_id)
        return user

    def get_user_by_email(self, user_email: str) -> User:
        query = self._build_user_query()
        user = User.objects.filter(email=user_email).filter(query).first()
        if user is None:
            raise UserEmailNotFoundException(user_email=user_email)
        return user

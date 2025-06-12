import uuid
from typing import Iterable

from django.db.models import Q
from django.utils import timezone
from psycopg2 import IntegrityError

from core.api.schemas.pagination import PaginationIn
from core.api.v1.users.schemas.filters import UserFilter
from core.api.v1.users.schemas.user_schemas import UserUpdateIn
from core.apps.common.exceptions.base_exception import ServiceException
from core.apps.common.exceptions.user_custom_exceptions.user_exc import (
    EmptyUpdateDataError,
    UserActiveDeleteError,
    UserCreationError,
    UserDeleteError,
    UserEmailNotFoundException,
    UserNotFoundException,
    UserUpdateError,
)
from core.apps.user.models import User
from core.apps.user.services.base_user_service import BaseUserService


class UserService(BaseUserService):
    def _build_user_query(self, filters: UserFilter | None = None) -> Q:
        """
        Формирует объект Q для фильтрации пользователей на основе заданных фильтров.

        Исключает суперпользователей и применяет поиск по имени, фамилии и email.

        Args:
            filters (UserFilter | None): Объект фильтрации с параметром поиска.

        Returns:
            Q: Объект Q для использования в QuerySet.
        """
        query = Q(is_superuser=False)

        if filters and filters.search is not None:
            query &= (
                Q(first_name__icontains=filters.search)
                | Q(last_name__icontains=filters.search)
                | Q(email__icontains=filters.search)
            )
        return query

    def get_user_by_id(self, user_id: uuid.UUID) -> User:
        """
        Получает пользователя по его уникальному идентификатору (UUID).

        Args:
            user_id (uuid.UUID): Уникальный идентификатор пользователя.

        Returns:
            User: Объект пользователя.

        Raises:
            UserNotFoundException: Если пользователь с указанным ID не найден.
        """
        query = self._build_user_query()
        user = User.objects.filter(id=user_id).filter(query).first()

        if user is None:
            raise UserNotFoundException(user_id=user_id)
        return user

    def get_user_by_email(self, user_email: str) -> User:
        """
        Получает пользователя по его адресу электронной почты.

        Args:
            user_email (str): Адрес электронной почты пользователя.

        Returns:
            User: Объект пользователя.

        Raises:
            UserEmailNotFoundException: Если пользователь с указанным email не найден.
        """
        query = self._build_user_query()
        user = User.objects.filter(email=user_email).filter(query).first()
        if user is None:
            raise UserEmailNotFoundException(user_email=user_email)
        return user

    def get_users_list(self, filters: UserFilter, pagination_in: PaginationIn) -> Iterable[User]:
        """
        Получает список активных (не удаленных) пользователей с фильтрацией и пагинацией.

        Предварительно загружает связанные подписки и тарифы.

        Args:
            filters (UserFilter): Объект фильтрации пользователей.
            pagination_in (PaginationIn): Объект с параметрами пагинации (offset, limit).

        Returns:
            Iterable[User]: Итерируемый объект пользователей.
        """
        query = self._build_user_query(filters)
        queryset = User.objects.filter(query)
        queryset = queryset.prefetch_related("user_subscription__tariff")
        users = queryset[pagination_in.offset : pagination_in.offset + pagination_in.limit]
        return users

    def get_users_count(self, filters: UserFilter) -> int:
        """
        Получает общее количество активных (не удаленных) пользователей с учетом фильтров.

        Args:
            filters (UserFilter): Объект фильтрации пользователей.

        Returns:
            int: Общее количество пользователей.
        """
        query = self._build_user_query(filters)
        return User.objects.filter(query).count()

    def get_all_users_archive(self, filters: UserFilter, pagination_in: PaginationIn) -> Iterable[User]:
        """
        Получает список архивированных (мягко удаленных и неактивных) пользователей
        с фильтрацией и пагинацией.

        Предварительно загружает связанные подписки и тарифы.

        Args:
            filters (UserFilter): Объект фильтрации пользователей.
            pagination_in (PaginationIn): Объект с параметрами пагинации (offset, limit).

        Returns:
            Iterable[User]: Итерируемый объект архивированных пользователей.
        """
        query = self._build_user_query(filters)
        queryset = User.objects.unfiltered().filter(query, is_deleted=True, is_active=False)
        queryset = queryset.prefetch_related("user_subscription__tariff")
        users = queryset[pagination_in.offset : pagination_in.offset + pagination_in.limit]
        return users

    def get_users_count_archive(self, filters: UserFilter) -> int:
        """
        Получает общее количество архивированных (мягко удаленных и неактивных) пользователей
        с учетом фильтров.

        Args:
            filters (UserFilter): Объект фильтрации пользователей.

        Returns:
            int: Общее количество архивированных пользователей.
        """
        query = self._build_user_query(filters)
        return User.objects.unfiltered().filter(query, is_deleted=True, is_active=False).count()

    def create_user(self, email: str, password: str, first_name: str, last_name: str, phone: str) -> User:
        """
        Создает нового пользователя.

        Args:
            email (str): Адрес электронной почты пользователя.
            password (str): Пароль пользователя.
            first_name (str): Имя пользователя.
            last_name (str): Фамилия пользователя.
            phone (str): Номер телефона пользователя.

        Returns:
            User: Созданный объект пользователя.

        Raises:
            UserCreationError: Если произошла ошибка при создании пользователя (например,
                               пользователь с таким email уже существует или ошибка БД).
        """
        try:
            user = User.objects.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                password=password,
            )
            return user
        except IntegrityError as e:
            if "unique constraint" in str(e).lower() and "email" in str(e).lower():
                raise UserCreationError(detail="Пользователь с таким email уже существует.")
            raise UserCreationError(detail=f"Ошибка базы данных при создании пользователя: {e}")
        except Exception as e:
            raise UserCreationError(detail=f"Неизвестная ошибка при создании пользователя: {e}")

    def user_update_full(
        self,
        user_id: uuid.UUID,
        user_data: UserUpdateIn,
    ) -> User:
        """
        Полностью обновляет данные пользователя по его ID.

        Обновляет все поля пользователя, включая email, имя, фамилию, телефон и пароль.

        Args:
            user_id (uuid.UUID): Уникальный идентификатор пользователя.
            user_data (UserUpdateIn): Pydantic-схема с полными данными для обновления.

        Returns:
            User: Обновленный объект пользователя.

        Raises:
            UserNotFoundException: Если пользователь не найден.
            UserCreationError: Если произошла ошибка базы данных (например, дубликат email)
                               или другая непредвиденная ошибка.
        """
        try:
            user = self.get_user_by_id(user_id=user_id)
            user.email = user_data.email
            user.first_name = user_data.first_name
            user.last_name = user_data.last_name
            user.phone = user_data.phone
            user.set_password(user_data.password)

            user.full_clean()
            user.save()
            return user
        except IntegrityError as e:
            if "unique constraint" in str(e).lower() and "email" in str(e).lower():
                raise UserUpdateError(detail="Пользователь с таким email уже существует.")
            raise UserUpdateError(detail=f"Ошибка базы данных при полном обновлении пользователя: {e}")
        except Exception as e:
            raise UserUpdateError(detail=f"Неизвестная ошибка при полном обновлении пользователя: {e}")

    def user_update_partial(self, user_id: uuid.UUID, user_data: UserUpdateIn) -> User:
        """
        Частично обновляет данные пользователя по его ID.

        Обновляет только те поля, которые были предоставлены в user_data.

        Args:
            user_id (uuid.UUID): Уникальный идентификатор пользователя.
            user_data (UserUpdateIn): Pydantic-схема с данными для частичного обновления.

        Returns:
            User: Обновленный объект пользователя.

        Raises:
            EmptyUpdateDataError: Если в user_data не было предоставлено данных для обновления.
            UserNotFoundException: Если пользователь не найден.
            UserCreationError: Если произошла ошибка базы данных (например, дубликат email)
                               или другая непредвиденная ошибка.
        """
        update_data = user_data.model_dump(exclude_unset=True)

        if not update_data:
            raise EmptyUpdateDataError()

        try:
            user = self.get_user_by_id(user_id=user_id)
            if "email" in update_data:
                user.email = update_data["email"]
            if "first_name" in update_data:
                user.first_name = update_data["first_name"]
            if "last_name" in update_data:
                user.last_name = update_data["last_name"]
            if "phone" in update_data:
                user.phone = update_data["phone"]

            if "password" in update_data:
                user.set_password(update_data["password"])

            user.full_clean()
            user.save()
            return user
        except UserNotFoundException:
            raise
        except IntegrityError as e:
            if "unique constraint" in str(e).lower() and "email" in str(e).lower():
                raise UserCreationError(detail="Пользователь с таким email уже существует.")
            raise UserUpdateError(detail=f"Ошибка базы данных при частичном обновлении пользователя: {e}")
        except Exception as e:
            raise UserUpdateError(detail=f"Неизвестная ошибка при частичном обновлении пользователя: {e}")

    def soft_delete_user(self, user_id: uuid.UUID) -> User:
        """
        Выполняет "мягкое" удаление пользователя, помечая его как удаленного и неактивного.

        Args:
            user_id (uuid.UUID): Уникальный идентификатор пользователя для мягкого удаления.

        Returns:
            User: Обновленный (мягко удаленный) объект пользователя.

        Raises:
            UserNotFoundException: Если пользователь не найден.
            UserDeleteError: Если произошла непредвиденная ошибка при мягком удалении.
        """
        try:
            user = self.get_user_by_id(user_id=user_id)

            user.is_deleted = True
            user.is_active = False
            user.deleted_at = timezone.now()

            user.full_clean()
            user.save()
            return user
        except IntegrityError as e:
            raise UserNotFoundException(detail=f"Ошибка базы данных при мягком удалении пользователя: {e}")
        except Exception as e:
            raise UserDeleteError(detail=f"Неизвестная ошибка при мягком удалении пользователя: {e}")

    def hard_delete_user(self, user_id: uuid.UUID) -> None:
        """
        Полностью удаляет пользователя из базы данных (без возможности восстановления).

        Args:
            user_id (uuid.UUID): Уникальный идентификатор пользователя для полного удаления.

        Raises:
            UserNotFoundException: Если пользователь не найден.
            UserActiveDeleteError: Если пользователь не помечен как мягко удаленный (is_deleted=False).
            UserDeleteError: Если произошла непредвиденная ошибка при полном удалении.
        """
        try:
            query = self._build_user_query()
            user = User.objects.unfiltered().filter(id=user_id).filter(query).first()

            if not user:
                raise UserNotFoundException(user_id=user_id)

            if user.is_deleted is False:
                raise UserActiveDeleteError()

            user.hard_delete()
            return None
        except ServiceException as e:  # Перехватываем свои ServiceException и перебрасываем, чтобы не потерять детали
            raise e
        except Exception as e:
            raise UserDeleteError(detail=f"Неизвестная ошибка при полном удалении пользователя: {e}")

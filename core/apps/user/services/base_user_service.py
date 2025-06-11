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
from core.api.v1.users.schemas.filters import UserFilter
from core.apps.user.models import User


class BaseUserService(ABC):

    @abstractmethod
    def create_user(self, email: str, password: str, first_name: str, last_name: str, phone: str = None) -> User:
        """
        Создает нового пользователя в системе.

        Args:
            email (str): Адрес электронной почты пользователя.
            password (str): Пароль пользователя.
            first_name (str): Имя пользователя.
            last_name (str): Фамилия пользователя.
            phone ([str]): Номер телефона пользователя (опционально).

        Returns:
            User: Созданный объект пользователя.
        """
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Получает пользователя по его уникальному ID.

        Args:
            user_id (uuid.UUID): Уникальный идентификатор пользователя.

        Returns:
            Optional[User]: Объект пользователя или None, если пользователь не найден.
        """
        pass

    @abstractmethod
    def get_user_by_email(self, user_email: str) -> Optional[User]:
        """
        Получает пользователя по его адресу электронной почты.

        Args:
            email (str): Адрес электронной почты пользователя.

        Returns:
            Optional[User]: Объект пользователя или None, если пользователь не найден.
        """
        pass

    # @abstractmethod
    # def soft_delete_user(self, user_id: uuid.UUID) -> None:
    #     """
    #     "Мягко" удаляет пользователя, устанавливая флаг is_deleted в True.

    #     Args:
    #         user_id (uuid.UUID): Уникальный идентификатор пользователя.
    #     """
    #     pass

    # @abstractmethod
    # def hard_delete_user(self, user_id: uuid.UUID) -> None:
    #     """
    #     Полностью удаляет пользователя из базы данных.
    #     Используйте этот метод с осторожностью, так как данные будут безвозвратно утеряны.

    #     Args:
    #         user_id (uuid.UUID): Уникальный идентификатор пользователя.
    #     """
    #     pass

    @abstractmethod
    def get_users_list(self, filters: UserFilter, pagination_in: PaginationIn) -> Iterator[User]:
        """
        Возвращает итерируемый объект QuerySet активных пользователей.

        Args:
            filters (UserFilter): Объект, содержащий параметры фильтрации пользователей.
            pagination_in (PaginationIn): Объект, содержащий параметры пагинации (offset, limit).

        Returns:
            Iterator[User]: Итератор по объектам пользователей.
        """
        pass

    @abstractmethod
    def get_users_count(self, filters: UserFilter) -> int:
        """
        Возвращает общее количество пользователей, соответствующих заданным фильтрам.

        Args:
            filters (UserFilter): Объект, содержащий параметры фильтрации пользователей.
            pagination_in (PaginationIn): Объект, содержащий параметры пагинации (offset, limit).
                                          Примечание: параметры пагинации не влияют на подсчет общего количества.

        Returns:
            int: Общее количество пользователей.
        """
        pass

    @abstractmethod
    def get_all_users_unfiltered(self, filters: UserFilter, pagination_in: PaginationIn) -> Iterable[User]:
        """
        Возвращает итерируемый объект QuerySet всех пользователей,
        включая "мягко" удаленных.

        Args:
            filters (UserFilter): Объект, содержащий параметры фильтрации пользователей.
            pagination_in (PaginationIn): Объект, содержащий параметры пагинации (offset, limit).

        Returns:
            Iterable[User]: Итерируемый объект по всем пользователям.
        """
        pass

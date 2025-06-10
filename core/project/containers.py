from functools import lru_cache

import punq

from core.apps.user.services.base_user_service import BaseUserService
from core.apps.user.services.user_service import UserService


@lru_cache(1)
def get_container() -> punq.Container:
    return _initialize_container()


def _initialize_container():
    container = punq.Container()
    container.register(BaseUserService, factory=lambda: UserService())
    return container

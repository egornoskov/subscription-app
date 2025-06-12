from functools import lru_cache

import punq

from core.apps.tariff.services.tarif_service import TariffService
from core.apps.tariff.services.tariff_base_service import TariffBaseService
from core.apps.user.services.base_user_service import BaseUserService
from core.apps.user.services.user_service import UserService


@lru_cache(1)
def get_container() -> punq.Container:
    return _initialize_container()


def _initialize_container():
    container = punq.Container()
    container.register(BaseUserService, factory=lambda: UserService())
    container.register(TariffBaseService, factory=lambda: TariffService())
    return container

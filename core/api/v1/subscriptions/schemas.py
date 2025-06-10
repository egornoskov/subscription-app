from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
)


class TariffOut(BaseModel):
    id: UUID = Field(
        ...,
        description="Уникальный идентификатор тарифа",
    )
    name: str = Field(
        ...,
        max_length=255,
        description="Название тарифа",
    )
    price: float = Field(
        ...,
        description="Цена тарифа",
    )

    class Config:
        from_attributes = True


class UserSubscriptionOut(BaseModel):
    id: UUID = Field(
        ...,
        description="Уникальный идентификатор подписки",
    )
    tariff: TariffOut = (Field(..., description="Информация о тарифе подписки"),)
    start_date: datetime = Field(
        ...,
        description="Дата начала подписки",
    )
    end_date: datetime = Field(
        ...,
        description="Дата окончания подписки",
    )
    is_active: bool = Field(
        ...,
        description="Статус активности подписки",
    )

    class Config:
        from_attributes = True

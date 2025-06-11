from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
)


class TariffCreateSchema(BaseModel):
    name: str = Field(
        ...,
        max_length=255,
        description="Название тарифа",
    )
    price: Decimal = Field(
        ...,
        description="Цена тарифа",
    )

    class Config:
        from_attributes = True


class TariffUpdateSchema(BaseModel):
    name: Optional[str] = Field(
        None,
        max_length=255,
        description="Название тарифа",
    )
    price: Optional[Decimal] = Field(
        None,
        description="Цена тарифа",
    )

    class Config:
        from_attributes = True


class UserSubscriptionOut(BaseModel):
    id: UUID = Field(
        ...,
        description="Уникальный идентификатор подписки",
    )
    tariff: TariffCreateSchema = (Field(..., description="Информация о тарифе подписки"),)
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

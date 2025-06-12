import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from core.api.v1.tariff.schemas.schemas import TariffCreateSchema


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

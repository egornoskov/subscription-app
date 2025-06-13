from uuid import UUID
from pydantic import BaseModel, Field


class SubscriptionCreate(BaseModel):
    user_id: UUID = Field(
        ...,
        description="Уникальный идентификатор пользователя",
    )
    tariff_id: UUID = Field(
        ...,
        description="Уникальный идентификатор тарифа",
    )
    month_duration: int = Field(
        ...,
        description="Продолжительность подписки в месяцах",
    )

    class Config:
        from_attributes = True


from decimal import Decimal
from typing import Optional

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

import uuid

from pydantic import (
    BaseModel,
    Field,
)


class OrderCreate(BaseModel):
    product_id: uuid.UUID = Field(
        ...,
        description="Уникальный идентификатор продукта",
    )
    user_id: uuid.UUID = Field(
        None,
        description="Уникальный идентификатор пользователя",
    )
    description: str | None = Field(
        None,
        description="Описание заказа",
    )

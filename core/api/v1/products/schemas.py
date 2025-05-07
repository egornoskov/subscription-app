from datetime import datetime
from pydantic import BaseModel


class ProductSchema(BaseModel):
    title: str
    discription: str
    created_at: datetime
    updated_at: datetime


ProductListSchema = list[ProductSchema]

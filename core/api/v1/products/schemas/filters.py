from pydantic import BaseModel


class OrderFilter(BaseModel):
    search: str | None = None

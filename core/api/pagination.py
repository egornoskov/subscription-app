from pydantic import (
    BaseModel,
    Field,
)


class PaginationOut(BaseModel):
    offset: int
    limit: int
    total: int


class PaginationIn(BaseModel):
    offset: int | None = 0
    limit: int = Field(default=20, ge=1, le=100)

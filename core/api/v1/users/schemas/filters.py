from pydantic import BaseModel


class UserFilter(BaseModel):
    search: str | None = None

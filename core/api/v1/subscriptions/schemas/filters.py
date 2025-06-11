from pydantic import BaseModel


class TariffFilter(BaseModel):
    search: str | None = None

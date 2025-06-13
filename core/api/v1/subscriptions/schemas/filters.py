from pydantic import BaseModel


class SubscriptionFilter(BaseModel):
    search: str | None = None

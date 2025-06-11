import uuid

from django.db import models

from core.apps.common.models import TimedBaseModel


class UserSubscription(TimedBaseModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        related_name="user_subscription",
    )
    tariff = models.ForeignKey(
        "subscription.Tariff",
        on_delete=models.CASCADE,
        related_name="tariff_subscription",
    )

    start_date = models.DateField()
    end_date = models.DateField()

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        unique_together = (
            "user",
            "tariff",
            "start_date",
        )

    def __str__(self):
        return f"{self.user} - {self.tariff}"


class Tariff(TimedBaseModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(
        max_length=100,
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    def __str__(self):
        return self.name

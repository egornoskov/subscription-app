import uuid

from django.db import models

from core.apps.common.models import TimedBaseModel


class Product(TimedBaseModel):
    id = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
    )
    title = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
    )
    description = models.TextField(
        null=True,
        blank=True,
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        db_table = "products"
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ("title",)

    def __str__(self):
        return self.title


class Order(TimedBaseModel):
    id = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="product_orders",
    )
    user = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        related_name="user_orders",
    )
    description = models.TextField(
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "В ожидании"),
            ("completed", "Завершен"),
            ("canceled", "Отменен"),
        ],
        default="pending",
    )

    class Meta:
        db_table = "orders"
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ("-created_at",)

    def __str__(self):
        return f"Order {self.id} for {self.product.title} by {self.user.id}, {self.user.email} - Status: {self.status}"

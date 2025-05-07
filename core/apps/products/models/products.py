from django.db import models

from core.apps.common.models import TimedBaseModel


class Product(TimedBaseModel):
    title = models.CharField(
        max_length=255,
        verbose_name="Название товара",
    )
    description = models.TextField(
        verbose_name="Описание товара",
        blank=True,
    )
    is_visible = models.BooleanField(
        default=True,
        verbose_name="Отображение на сайте",
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

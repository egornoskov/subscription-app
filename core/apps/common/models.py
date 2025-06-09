from django.db import models
from django.utils import timezone

from core.apps.common.managers import IsDeletedManager


class TimedBaseModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата изменения",
    )
    is_deleted = models.BooleanField(
        default=False,
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-id"]  # New
        abstract = True

    objects = IsDeletedManager()

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

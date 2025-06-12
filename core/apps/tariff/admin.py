from django.contrib import admin

from .models import (
    Tariff,
)


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ("name", "price")
    search_fields = ("name",)
    ordering = ("price",)

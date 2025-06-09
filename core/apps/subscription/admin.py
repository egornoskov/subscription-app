from django.contrib import admin

from .models import (
    Tariff,
    UserSubscription,
)


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ("name", "price")
    search_fields = ("name",)
    ordering = ("price",)


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "tariff", "start_date", "end_date")
    search_fields = ("user__email", "tariff__name")
    list_filter = ("tariff", "start_date", "end_date")
    autocomplete_fields = ("user", "tariff")

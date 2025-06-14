from django.contrib import admin

from .models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "tariff", "start_date", "end_date")
    search_fields = ("user__email", "tariff__name")
    list_filter = ("tariff", "start_date", "end_date")
    autocomplete_fields = ("user", "tariff")

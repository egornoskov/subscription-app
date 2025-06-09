from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "first_name", "last_name", "phone", "is_staff", "is_superuser", "subscriptions_overview")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Личная информация", {"fields": ("first_name", "last_name", "phone")}),
        ("Права доступа", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "password"),
            },
        ),
    )
    search_fields = ("email", "first_name", "last_name", "phone")
    ordering = ("email",)

    def subscriptions_overview(self, obj):
        subscriptions = obj.subscriptions.all()
        if subscriptions:
            return ", ".join([sub.name for sub in subscriptions])
        return "Нет подписок"

    subscriptions_overview.short_description = "Подписки"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related("subscriptions")
        return qs

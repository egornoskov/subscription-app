from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm

from core.apps.subscriptions.models import Subscription

from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phone")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["phone"].required = False


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 1
    fields = ("tariff", "start_date", "end_date")
    verbose_name = "Подписка"
    verbose_name_plural = "Подписки"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (SubscriptionInline,)
    add_form = CustomUserCreationForm
    list_display = ("email", "first_name", "last_name", "phone", "is_staff", "subscriptions_overview", "is_active")
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
                "fields": ("email", "first_name", "last_name", "phone", "password1", "password2"),
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


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 1
    fields = ("tariff", "start_date", "end_date")
    verbose_name = "Подписка"
    verbose_name_plural = "Подписки"

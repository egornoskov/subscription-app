from django.utils import timezone
import uuid

from django.contrib.auth.models import (
    AbstractUser,
    Group,
    Permission,
)
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.apps.common.models import TimedBaseModel
from core.apps.user.managers import CustomUserManager


class User(AbstractUser, TimedBaseModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    username = None

    first_name = models.CharField(
        max_length=30,
        verbose_name="Имя",
    )
    last_name = models.CharField(
        max_length=30,
        verbose_name="Фамилия",
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Почта",
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    is_staff = models.BooleanField(
        default=False,
        verbose_name="Права администратора",
    )

    is_active = models.BooleanField(
        default=False,
        verbose_name="Активен",
    )
    telegram_id = models.BigIntegerField(
        unique=True,
        verbose_name="ID в Telegram",
        blank=True,
        null=True,
    )

    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Номер телефона должен быть в формате: '+999999999'. До 15 цифр.",
    )

    phone = models.CharField(
        validators=[phone_regex],
        max_length=20,
        verbose_name="Телефон",
        blank=True,
        null=True,
    )

    subscriptions = models.ManyToManyField(
        "tariff.Tariff",
        through="subscriptions.Subscription",
        related_name="subscribed_users",
        verbose_name="Подписки",
    )
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will get all permissions " "granted to each of their groups."
        ),
        verbose_name=_("groups"),
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_set_permissions",
        blank=True,
        help_text=_("Specific permissions for this user."),
        verbose_name=_("user permissions"),
        related_query_name="user",
    )

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-id"]
        db_table = "users"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name

    @property
    def has_active_subscription(self) -> bool:
        """
        Проверяет, есть ли у пользователя действующая активная подписка.
        """
        return self.user_subscription.filter(
            is_active=True,
            end_date__gte=timezone.now(),
            is_deleted=False,
        ).exists()

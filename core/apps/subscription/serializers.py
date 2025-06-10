from rest_framework import serializers

from core.apps.subscription.models import (
    Tariff,
    UserSubscription,
)


class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = ("id", "name", "price")


class UserSubscriptionSerializer(serializers.ModelSerializer):
    tariff = TariffSerializer(
        read_only=True,
    )

    class Meta:
        model = UserSubscription
        fields = (
            "id",
            "user",
            "tariff",
            "start_date",
            "end_date",
            "is_active",
        )
        read_only_fields = (
            "id",
            "user",
            "is_active",
            "start_date",
            "end_date",
        )

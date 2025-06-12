from rest_framework import serializers

from core.apps.tariff.models import (
    Tariff,
)

from core.apps.subscriptions.models import UserSubscription


class UserSubscriptionSerializer(serializers.ModelSerializer):
    tariff = serializers.PrimaryKeyRelatedField(
        queryset=Tariff.objects.all(),
    )

    class Meta:
        model = UserSubscription
        fields = (
            "id",
            "tariff",
            "start_date",
            "end_date",
            "is_active",
        )
        read_only_fields = (
            "id",
            "is_active",
            "start_date",
            "end_date",
        )

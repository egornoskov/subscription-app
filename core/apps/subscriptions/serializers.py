from rest_framework import serializers

from core.apps.tariff.models import (
    Tariff,
)

from core.apps.subscriptions.models import Subscription
from core.apps.tariff.serializers import TariffSerializer
from core.apps.user.models import User


class SubscriptionSerializer(serializers.ModelSerializer):
    tariff_details = TariffSerializer(source="tariff", read_only=True)
    tariff = serializers.PrimaryKeyRelatedField(queryset=Tariff.objects.all(), write_only=True)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Subscription
        fields = (
            "id",
            "tariff_details",
            "tariff",
            "start_date",
            "end_date",
            "is_active",
            'user',
        )
        read_only_fields = (
            "id",
            "is_active",
            "start_date",
            "end_date",
        )

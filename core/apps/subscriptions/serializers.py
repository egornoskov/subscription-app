from rest_framework import serializers

from core.apps.subscriptions.models import Subscription
from core.apps.tariff.models import Tariff
from core.apps.tariff.serializers import TariffSerializer


class SubscriptionSerializer(serializers.ModelSerializer):
    tariff_details = TariffSerializer(source="tariff", read_only=True)

    tariff = serializers.PrimaryKeyRelatedField(
        queryset=Tariff.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
        help_text="UUID тарифа.",
    )

    end_date = serializers.DateField(
        required=False,
        allow_null=True,
        help_text="Дата окончания подписки.",
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
        )
        read_only_fields = (
            "id",
            "start_date",
            "is_active",
        )

from rest_framework import serializers

from core.apps.tariff.models import (
    Tariff,
)


class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = ("id", "name", "price")

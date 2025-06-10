from rest_framework import serializers

from core.apps.subscription.serializers import UserSubscriptionSerializer
from core.apps.user.models import User


class UserSerializer(serializers.ModelSerializer):
    subscription = UserSubscriptionSerializer(
        read_only=True,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "email",
            "phone",
            "is_active",
            "subscription",
        )
        read_only_fields = (
            "id",
            "subscription",
        )

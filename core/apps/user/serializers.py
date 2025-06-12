from rest_framework import serializers

from core.apps.subscriptions.serializers import UserSubscriptionSerializer
from core.apps.user.models import User


class UserSerializer(serializers.ModelSerializer):
    subscriptions_details = UserSubscriptionSerializer(
        source="user_subscription",
        many=True,
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
            "subscriptions_details",
        )
        read_only_fields = (
            "id",
            "full_name",
            "subscriptions_details",
        )

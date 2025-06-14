from rest_framework import serializers

from core.apps.products.models import Order
from core.apps.subscriptions.serializers import SubscriptionSerializer
from core.apps.user.serializers import UserSerializer
from core.apps.subscriptions.models import Subscription
from core.apps.user.models import User


class UserOrderSerializer(serializers.ModelSerializer):
    subscription_details = SubscriptionSerializer(
        source="subscription",
        read_only=True,
    )
    user_details = UserSerializer(
        source="user",
        read_only=True,
    )

    subscription = serializers.PrimaryKeyRelatedField(
        queryset=Subscription.objects.all(),
        write_only=True,
    )
    description = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    status = serializers.ChoiceField(
        choices=Order.status.field.choices,
        required=False,
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "subscription_details",
            "user_details",
            "subscription",
            "description",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user_details",
            "created_at",
            "updated_at",
        )


class AdminOrderSerializer(UserOrderSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
    )
    status = serializers.ChoiceField(
        choices=Order.status.field.choices,
        required=False,
    )

    class Meta(UserOrderSerializer.Meta):
        fields = UserOrderSerializer.Meta.fields + ("user",)
        read_only_fields = tuple(f for f in UserOrderSerializer.Meta.read_only_fields if f != "user_details")

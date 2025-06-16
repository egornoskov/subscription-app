from rest_framework import serializers

from core.apps.products.models import Order
from core.apps.subscriptions.models import Subscription
from core.apps.subscriptions.serializers import SubscriptionSerializer
from core.apps.user.serializers import UserSerializer


class UserOrderSerializer(serializers.ModelSerializer):
    subscription_details = SubscriptionSerializer(
        source="subscription",
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
            "subscription",
            "description",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class AdminOrderSerializer(UserOrderSerializer):
    subscription_details = SubscriptionSerializer(
        source="subscription",
        read_only=True,
    )
    user_details = UserSerializer(
        source="user",
        read_only=True,
    )
    status = serializers.ChoiceField(
        choices=Order.status.field.choices,
        required=False,
    )

    class Meta(UserOrderSerializer.Meta):
        fields = UserOrderSerializer.Meta.fields + ("user_details",)
        read_only_fields = UserOrderSerializer.Meta.read_only_fields + ("user_details",)


class OrderUpdateSerializer(serializers.Serializer):
    """
    Сериализатор для обновления поля 'description' заказа.
    """

    description = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=500,
    )

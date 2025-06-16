from rest_framework import serializers

from core.apps.subscriptions.serializers import SubscriptionSerializer
from core.apps.user.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone",
            "password",
            "password2",
        )
        extra_kwargs = {
            "email": {
                "required": True,
            },
            "first_name": {
                "required": True,
            },
            "last_name": {
                "required": True,
            },
            "phone": {
                "required": True,
                "error_messages": {"required": "Номер телефона обязателен для регистрации."},
            },
        }

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Пароли должны совпадать."})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"],
            phone=validated_data["phone"],
            is_active=False,
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    subscriptions_details = SubscriptionSerializer(
        source="user_subscriptions_details",
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

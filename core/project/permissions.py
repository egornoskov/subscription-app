from uuid import UUID as PyUUID  # Для работы с UUID из URL

from django.conf import settings
from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Разрешает доступ только администраторам (is_staff=True).
    """

    message = "У вас нет прав администратора."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsAccountActivated(permissions.BasePermission):
    """
    Разрешает доступ только активированным пользователям (is_active=True).
    """

    message = "Ваш аккаунт не активирован. Пожалуйста, завершите активацию через Telegram."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active


class IsResourceOwner(permissions.BasePermission):
    """
    Разрешает доступ только владельцу ресурса.
    Применяется для детальных операций (retrieve, update, destroy).
    """

    message = "Вы не являетесь владельцем этого ресурса."

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsUserOwnerOrAdmin(permissions.BasePermission):
    """
    Кастомное разрешение: разрешает доступ, если пользователь является владельцем профиля
    (UUID аутентифицированного пользователя совпадает с UUID из URL) ИЛИ является админом.
    Требует аутентификации.
    """

    message = "У вас нет прав для выполнения этого действия или вы не являетесь владельцем этого профиля."

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated and request.user.is_staff:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        requested_user_uuid_str = view.kwargs.get("user_uuid")
        if not requested_user_uuid_str:
            self.message = "UUID пользователя не найден в запросе."
            return False

        try:
            requested_user_uuid = PyUUID(requested_user_uuid_str)
        except ValueError:
            self.message = "Некорректный формат UUID пользователя в URL."
            return False

        return request.user.uuid == requested_user_uuid


class IsBotApiKeyAuthenticated(permissions.BasePermission):
    """
    Пользователь (или в данном случае бот) должен быть аутентифицирован
    с помощью специального API-ключа в заголовке 'X-Bot-Api-Key'.
    """

    def has_permission(self, request, view):
        bot_api_key = request.headers.get("X-Bot-Api-Key")
        return bot_api_key == settings.BOT_API_KEY

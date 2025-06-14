# core/permissions.py

from rest_framework import permissions
from uuid import UUID as PyUUID  # Для работы с UUID из URL


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


class HasActiveSubscription(permissions.BasePermission):
    """
    Разрешает доступ только пользователям с активной подпиской.
    Требует реализации свойства `has_active_subscription` в модели User.
    """

    message = "Для выполнения этого действия требуется активная подписка."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.has_active_subscription


class IsResourceOwner(permissions.BasePermission):
    """
    Разрешает доступ только владельцу ресурса.
    Применяется для детальных операций (retrieve, update, destroy).
    """

    message = "Вы не являетесь владельцем этого ресурса."

    def has_object_permission(self, request, view, obj):
        # Этот класс проверяет, есть ли у объекта атрибут 'user' и совпадает ли он с request.user.
        # Для UserDetailActionsView мы используем user_uuid из kwargs, поэтому нужен другой подход.
        return obj.user == request.user


class IsUserOwnerOrAdmin(permissions.BasePermission):
    """
    Кастомное разрешение: разрешает доступ, если пользователь является владельцем профиля
    (UUID аутентифицированного пользователя совпадает с UUID из URL) ИЛИ является админом.
    Требует аутентификации.
    """

    message = "У вас нет прав для выполнения этого действия или вы не являетесь владельцем этого профиля."

    def has_permission(self, request, view):
        # Всегда разрешаем администраторам
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

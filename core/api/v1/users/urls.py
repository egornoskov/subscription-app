from django.urls import path

from core.api.v1.users.handlers import (
    UserListCreateView,
    UserDetailActionsView,
    UserHardDeleteView,
    ArchivedUserListView,
)


app_name = "users"

urlpatterns = [
    path(
        "users/",
        UserListCreateView.as_view(),
        name="user-list-create",
    ),
    path(
        "users/<uuid:user_uuid>/",
        UserDetailActionsView.as_view(),
        name="user-detail-actions",
    ),
    path(
        "users/<uuid:user_uuid>/hard-delete/",
        UserHardDeleteView.as_view(),
        name="user-hard-delete",
    ),
    path(
        "users/archive/",
        ArchivedUserListView.as_view(),
        name="user-archive-list",
    ),
]

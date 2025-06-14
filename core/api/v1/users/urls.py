from django.urls import path

from core.api.v1.users.handlers import (
    ArchivedUserListView,
    UserDetailActionsView,
    UserHardDeleteView,
    UserListCreateView,
)


app_name = "users"

urlpatterns = [
    path(
        "",
        UserListCreateView.as_view(),
        name="user-list-create",
    ),
    path(
        "<uuid:user_uuid>/",
        UserDetailActionsView.as_view(),
        name="user-detail-actions",
    ),
    path(
        "<uuid:user_uuid>/hard-delete/",
        UserHardDeleteView.as_view(),
        name="user-hard-delete",
    ),
    path(
        "archive/",
        ArchivedUserListView.as_view(),
        name="user-archive-list",
    ),
]

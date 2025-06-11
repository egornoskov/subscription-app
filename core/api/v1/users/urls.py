from django.urls import path

from core.api.v1.users.handlers import (
    ArchiveUserListView,
    UserCreateView,
    UserHardDeleteView,
    UserListView,
    UserPartialUpdateView,
    UserRetriveByEmailView,
    UserRetriveByIdView,
    UserSoftDeleteView,
    UserUpdateView,
)


app_name = "users"

urlpatterns = [
    path(
        "create/",
        UserCreateView.as_view(),
        name="create-user",
    ),
    path(
        "",
        UserListView.as_view(),
        name="users-list",
    ),
    path(
        "detail_uuid/<uuid:user_uuid>/",
        UserRetriveByIdView.as_view(),
        name="user-detail-by-id",
    ),
    path(
        "detail_email/<str:user_email>/",
        UserRetriveByEmailView.as_view(),
        name="user-detail-by-email",
    ),
    path(
        "update/<uuid:user_uuid>/",
        UserUpdateView.as_view(),
        name="update-user",
    ),
    path(
        "partial_update/<uuid:user_uuid>/",
        UserPartialUpdateView.as_view(),
        name="partial-update-user",
    ),
    path(
        "soft_delete/<uuid:user_uuid>/",
        UserSoftDeleteView.as_view(),
        name="soft-delete-user",
    ),
    path(
        "hard_delete/<uuid:user_uuid>/",
        UserHardDeleteView.as_view(),
        name="hard-delete-user",
    ),
    path(
        "archive/",
        ArchiveUserListView.as_view(),
        name="archive-users",
    ),
]

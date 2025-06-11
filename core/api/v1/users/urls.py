from django.urls import path

from core.api.v1.users.handlers import (
    UserCreateView,
    UserListView,
    UserRetriveByEmailView,
    UserRetriveByIdView,
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
]

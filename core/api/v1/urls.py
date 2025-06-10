from django.urls import path

from core.api.v1.users.handlers import (
    UserListView,
    UserRetriveByEmailView,
    UserRetriveByIdView,
)


app_name = "v1"
urlpatterns = [
    path(
        "users/",
        UserListView.as_view(),
        name="users",
    ),
    path(
        "<uuid:user_uuid>/",
        UserRetriveByIdView.as_view(),
        name="user-detail-by-id",
    ),
    path(
        "<str:user_email>/",
        UserRetriveByEmailView.as_view(),
        name="user-detail-by-email>",
    ),
]

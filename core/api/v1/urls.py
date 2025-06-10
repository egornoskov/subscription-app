from django.urls import path

from core.api.v1.users.handlers import UserListView


app_name = "v1"
urlpatterns = [
    path("users/", UserListView.as_view(), name="users"),
]

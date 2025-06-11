from django.urls import (
    include,
    path,
)


app_name = "v1"

urlpatterns = [
    path("v1/users/", include("core.api.v1.users.urls")),
]

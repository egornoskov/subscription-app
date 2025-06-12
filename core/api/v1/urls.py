from django.urls import (
    include,
    path,
)


app_name = "v1"

urlpatterns = [
    path("v1/users/", include("core.api.v1.users.urls")),
    path("v1/tariff/", include("core.api.v1.tariff.urls")),
]

from django.urls import (
    include,
    path,
)


urlpatterns = [
    path("", include("core.api.v1.urls")),
]

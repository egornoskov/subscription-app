from django.urls import path

from core.api.v1.tariff.handlers import (
    TariffListCreateView,  # Объединенный класс
    TariffDetailActionsView,
)


app_name = "tariff"

urlpatterns = [
    path(
        "",
        TariffListCreateView.as_view(),
        name="tariff-list-create",
    ),
    path(
        "<uuid:tariff_uuid>/",
        TariffDetailActionsView.as_view(),
        name="tariff-detail-actions",
    ),
]

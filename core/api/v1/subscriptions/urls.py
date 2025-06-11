from django.urls import path

from core.api.v1.subscriptions.tariff_handlers import (
    TariffCreationView,
    TariffListView,
    TariffDetailActionsView,
)


app_name = "tariff"

urlpatterns = [
    path(
        "tariff/",
        TariffListView.as_view(),
        name="tariff-list",
    ),
    path(
        "tariff/create/",
        TariffCreationView.as_view(),
        name="tariff-create",
    ),
    path(
        "tariff/<uuid:tariff_uuid>/",
        TariffDetailActionsView.as_view(),
        name="tariff-detail-actions",
    ),
]

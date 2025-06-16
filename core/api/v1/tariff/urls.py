from django.urls import path

from core.api.v1.tariff.handlers import (
    HardDeleteTariffView,
    TariffArchiveListView,
    TariffDetailActionsView,
    TariffListCreateView,
)


app_name = "tariff"

urlpatterns = [
    path(
        "",
        TariffListCreateView.as_view(),
        name="tariff-list-create",
    ),
    path(
        "archive/",
        TariffArchiveListView.as_view(),
        name="tariff-archive-list",
    ),
    path(
        "<uuid:tariff_uuid>/hard-delete/",
        HardDeleteTariffView.as_view(),
        name="tariff-hard-delete",
    ),
    path(
        "<uuid:tariff_uuid>/",
        TariffDetailActionsView.as_view(),
        name="tariff-detail-actions",
    ),
]

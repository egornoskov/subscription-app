from django.urls import path

from core.api.v1.subscriptions.tariff_handlers import (
    TariffListCreateView,  # Объединенный класс
    TariffDetailActionsView,
)


app_name = "tariff"

urlpatterns = [
    path(
        "tariff/",
        TariffListCreateView.as_view(),  # Используем объединенный класс для списка и создания
        name="tariff-list-create",
    ),
    path(
        "tariff/<uuid:tariff_uuid>/",
        TariffDetailActionsView.as_view(),
        name="tariff-detail-actions",
    ),
]

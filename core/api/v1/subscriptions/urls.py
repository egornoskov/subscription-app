from django.urls import path
from core.api.v1.subscriptions.tariff_handlers import TariffListView

app_name = "tariff"

urlpatterns = [
    path("tariffs/", TariffListView.as_view(), name="tariff-list"),
]

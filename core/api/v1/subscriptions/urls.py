from django.urls import path

from core.api.v1.subscriptions.handlers import (
    SubscriptionDetailActionsView,
    SubscriptionsListCreateView,
)


app_name = "subscriptions"

urlpatterns = [
    path(
        "",
        SubscriptionsListCreateView.as_view(),
        name="subscriptions-list-create",
    ),
    path(
        "<uuid:subscription_uuid>/",
        SubscriptionDetailActionsView.as_view(),
        name="subscription-detail-actions",
    ),
]

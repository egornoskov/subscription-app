from django.urls import path

from core.api.v1.subscriptions.handlers import (
    ArchiveListSubscriptionView,
    HardDeleteSubscriptionView,
    SubscriptionDetailActionsView,
    SubscriptionsListCreateView,
)


app_name = "subscriptions"

urlpatterns = [
    path(
        "archive/",
        ArchiveListSubscriptionView.as_view(),
        name="subscription-archive-list",
    ),
    path(
        "<uuid:subscription_uuid>/hard-delete/",
        HardDeleteSubscriptionView.as_view(),
        name="subscription-hard-delete",
    ),
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

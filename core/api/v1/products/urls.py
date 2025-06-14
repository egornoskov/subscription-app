from django.urls import path


from core.api.v1.products.handlers import OrderListCreateView, OrderDetailActionView


app_name = "orders"

urlpatterns = [
    path(
        "",
        OrderListCreateView.as_view(),
        name="order-list-create",
    ),
    path(
        "<uuid:order_id>/",
        OrderDetailActionView.as_view(),
        name="order-detail-action",
    ),
]

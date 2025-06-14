from django.urls import path


from core.api.v1.products.handlers import OrderListCreateView


app_name = "orders"

urlpatterns = [
    path(
        "",
        OrderListCreateView.as_view(),
        name="order-list-create",
    ),
]

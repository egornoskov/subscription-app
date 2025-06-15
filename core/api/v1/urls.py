from django.urls import (
    include,
    path,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from core.api.v1.handlers import RegisterUserView

app_name = "v1"

urlpatterns = [
    path(
        "v1/register/",
        RegisterUserView.as_view(),
        name="register",
    ),
    # path(
    #     "v1/activate-telegram-user/",
    #     ActivateUserAPIView.as_view(),
    #     name="activate-telegram-user",
    # ),
    path(
        "v1/login/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "v1/login/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "v1/login/verify/",
        TokenVerifyView.as_view(),
        name="token_verify",
    ),
    path(
        "v1/users/",
        include("core.api.v1.users.urls"),
    ),
    path(
        "v1/tariff/",
        include("core.api.v1.tariff.urls"),
    ),
    path(
        "v1/subscriptions/",
        include("core.api.v1.subscriptions.urls"),
    ),
    path(
        "v1/orders/",
        include("core.api.v1.products.urls"),
    ),
]

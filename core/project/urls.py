from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib import admin

# Existing URLs
urlpatterns = [
    path("api/", include("core.api.urls")),
    # Other routes, e.g., admin
    path("admin/", admin.site.urls),
]

# Configure Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Subscriptions API",
        default_version="v1",
        description="API for managing subscriptions",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Add Swagger routes
urlpatterns += [
    path("docs/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

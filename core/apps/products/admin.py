from django.contrib import admin
from .models import Order, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "description")
    ordering = ("-created_at",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "status", "created_at")
    list_filter = ("status", "created_at", "user", "product")
    search_fields = ("id__contains", "description", "user__email", "product__title")
    ordering = ("-created_at",)
    raw_id_fields = ("user", "product")

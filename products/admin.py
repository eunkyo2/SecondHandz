from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "seller", "price", "is_blocked", "is_sold", "created_at")
    list_filter = ("is_blocked", "is_sold")
    search_fields = ("title",)

from django.contrib import admin

from accounts.models import User
from products.models import Product

from .models import Report


@admin.action(description="선택한 신고의 대상을 차단하고 처리완료로 표시")
def block_target_and_resolve(modeladmin, request, queryset):
    for report in queryset:
        if report.target_type == "user":
            User.objects.filter(pk=report.target_id).update(is_banned=True)
        else:
            Product.objects.filter(pk=report.target_id).update(is_blocked=True)
    queryset.update(status="resolved")


@admin.action(description="처리완료로 표시")
def mark_resolved(modeladmin, request, queryset):
    queryset.update(status="resolved")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("target_type", "target_id", "reporter", "status", "created_at")
    list_filter = ("status", "target_type")
    actions = [block_target_and_resolve, mark_resolved]

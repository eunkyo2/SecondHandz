from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from accounts.models import User
from products.models import Product

from .forms import ReportForm
from .models import Report

REPORT_THRESHOLD = 7


@login_required
def report_create(request):
    if request.method == "POST":
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            target_type = form.cleaned_data["target_type"]
            target_id = form.cleaned_data["target_id"]
            if Report.objects.filter(
                reporter=request.user, target_type=target_type, target_id=target_id, status="pending"
            ).exists():
                messages.error(request, "이미 신고가 접수되어 검토 중입니다.")
                return redirect("home")
            report = form.save(commit=False)
            report.reporter = request.user
            report.save()
            _auto_moderate(target_type, target_id)
            messages.success(request, "신고가 접수되었습니다.")
            return redirect("home")
    else:
        form = ReportForm(initial={
            "target_type": request.GET.get("target_type", ""),
            "target_id": request.GET.get("target_id", ""),
        })
    return render(request, "reports/form.html", {"form": form})


def _auto_moderate(target_type, target_id):
    pending_count = Report.objects.filter(
        target_type=target_type, target_id=target_id, status="pending"
    ).count()
    if pending_count < REPORT_THRESHOLD:
        return
    if target_type == "product":
        Product.objects.filter(pk=target_id).update(is_blocked=True)
    else:
        User.objects.filter(pk=target_id).update(is_dormant=True)
    Report.objects.filter(target_type=target_type, target_id=target_id, status="pending").update(status="resolved")


@login_required
def report_list(request):
    if not request.user.is_staff:
        raise PermissionDenied
    reports = Report.objects.select_related("reporter").order_by("-created_at")

    user_ids = [r.target_id for r in reports if r.target_type == "user"]
    product_ids = [r.target_id for r in reports if r.target_type == "product"]
    users_by_id = User.objects.in_bulk(user_ids)
    products_by_id = Product.objects.in_bulk(product_ids)

    items = []
    for r in reports:
        target = users_by_id.get(r.target_id) if r.target_type == "user" else products_by_id.get(r.target_id)
        items.append({"report": r, "target": target})

    return render(request, "reports/list.html", {"items": items})

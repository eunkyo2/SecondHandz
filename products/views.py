from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm
from .models import Product


def product_list(request):
    query = request.GET.get("q", "").strip()[:100]
    products = Product.objects.filter(is_blocked=False, is_sold=False).order_by("-created_at")
    if query:
        products = products.filter(title__icontains=query)
    return render(request, "products/list.html", {"products": products, "query": query})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_blocked=False)
    return render(request, "products/detail.html", {"product": product})


@login_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect("product_detail", pk=product.pk)
    else:
        form = ProductForm()
    return render(request, "products/form.html", {"form": form})


@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.seller != request.user:
        raise PermissionDenied
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect("product_detail", pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, "products/form.html", {"form": form, "editing": True})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.seller != request.user:
        raise PermissionDenied
    if request.method == "POST":
        product.delete()
        return redirect("product_list")
    return render(request, "products/confirm_delete.html", {"product": product})


@login_required
def toggle_sold(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.seller != request.user:
        raise PermissionDenied
    if request.method == "POST":
        product.is_sold = not product.is_sold
        product.save(update_fields=["is_sold"])
    return redirect("product_detail", pk=product.pk)


@login_required
def buy(request, pk):
    product = get_object_or_404(Product, pk=pk, is_blocked=False, is_sold=False)
    return redirect("chat_start", product_id=product.pk)


@login_required
def blocked_list(request):
    if not request.user.is_staff:
        raise PermissionDenied
    products = Product.objects.filter(is_blocked=True).select_related("seller").order_by("-created_at")
    return render(request, "products/blocked_list.html", {"products": products})


@login_required
def product_unblock(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied
    if request.method == "POST":
        Product.objects.filter(pk=pk).update(is_blocked=False)
        messages.success(request, "차단이 해제되었습니다.")
    return redirect("product_blocked_list")

from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, ProfileForm, SignupForm, TransferForm
from .models import User


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("home")
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})


class AccountLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm


def logout_view(request):
    auth_logout(request)
    return redirect("home")


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_owner = request.user.is_authenticated and request.user == profile_user
    products = profile_user.products.all() if is_owner else profile_user.products.filter(is_blocked=False)

    form = None
    password_form = None
    transfer_form = None

    if is_owner:
        if request.method == "POST":
            form = ProfileForm(request.POST, request.FILES, instance=profile_user)
            if form.is_valid():
                form.save()
                messages.success(request, "프로필이 업데이트되었습니다.")
                return redirect("profile", username=profile_user.username)
        else:
            form = ProfileForm(instance=profile_user)
        password_form = PasswordChangeForm(profile_user)
    elif request.user.is_authenticated:
        transfer_form = TransferForm()

    return render(request, "accounts/profile.html", {
        "profile_user": profile_user,
        "is_owner": is_owner,
        "products": products,
        "form": form,
        "password_form": password_form,
        "transfer_form": transfer_form,
    })


@login_required
def change_password(request, username):
    if request.user.username != username:
        raise PermissionDenied
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "비밀번호가 변경되었습니다.")
        else:
            messages.error(request, "비밀번호를 변경하지 못했습니다: " + " ".join(
                e for errs in form.errors.values() for e in errs
            ))
    return redirect("profile", username=username)


@login_required
def dormant_list(request):
    if not request.user.is_staff:
        raise PermissionDenied
    users = User.objects.filter(is_dormant=True).order_by("username")
    return render(request, "accounts/dormant_list.html", {"users": users})


@login_required
def dormant_restore(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied
    if request.method == "POST":
        User.objects.filter(pk=pk).update(is_dormant=False)
        messages.success(request, "휴면 상태가 해제되었습니다.")
    return redirect("dormant_list")


@login_required
def transfer(request, username):
    recipient = get_object_or_404(User, username=username)
    if recipient == request.user:
        raise PermissionDenied
    if request.method == "POST":
        form = TransferForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            with transaction.atomic():
                sender = User.objects.select_for_update().get(pk=request.user.pk)
                target = User.objects.select_for_update().get(pk=recipient.pk)
                if sender.balance < amount:
                    messages.error(request, "잔액이 부족합니다.")
                else:
                    sender.balance -= amount
                    target.balance += amount
                    sender.save(update_fields=["balance"])
                    target.save(update_fields=["balance"])
                    messages.success(request, f"{target.username}님에게 {amount}원을 송금했습니다.")
        else:
            messages.error(request, "올바른 금액을 입력해주세요.")
    return redirect("profile", username=username)

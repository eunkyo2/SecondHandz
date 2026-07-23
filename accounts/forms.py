from datetime import timedelta

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import User, generate_random_nickname

RESERVED_USERNAMES = {"login", "signup", "logout"}
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=5)


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def clean_username(self):
        username = self.cleaned_data["username"]
        if username.lower() in RESERVED_USERNAMES:
            raise ValidationError("사용할 수 없는 아이디입니다.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.nickname = generate_random_nickname()
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get("username")
        user = User.objects.filter(username=username).first() if username else None

        if user and user.locked_until and user.locked_until > timezone.now():
            raise ValidationError("로그인 시도가 너무 많습니다. 잠시 후 다시 시도해주세요.", code="locked")

        try:
            cleaned_data = super().clean()
        except ValidationError as exc:
            if user and getattr(exc, "code", None) == "invalid_login":
                user.failed_attempts += 1
                if user.failed_attempts >= MAX_FAILED_ATTEMPTS:
                    user.locked_until = timezone.now() + LOCKOUT_DURATION
                    user.failed_attempts = 0
                user.save(update_fields=["failed_attempts", "locked_until"])
            raise

        if user:
            user.failed_attempts = 0
            user.locked_until = None
            user.save(update_fields=["failed_attempts", "locked_until"])
        return cleaned_data

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.is_banned:
            raise ValidationError("차단된 계정입니다.", code="banned")
        if user.is_dormant:
            raise ValidationError("신고 누적으로 휴면 처리된 계정입니다. 관리자에게 문의하세요.", code="dormant")


class ProfileForm(forms.ModelForm):
    current_password = forms.CharField(widget=forms.PasswordInput, required=False, label="현재 비밀번호(아이디 변경 시 필요)")

    class Meta:
        model = User
        fields = ("username", "nickname", "bio", "profile_image")

    def clean_username(self):
        username = self.cleaned_data["username"]
        if username.lower() in RESERVED_USERNAMES:
            raise ValidationError("사용할 수 없는 아이디입니다.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        new_username = cleaned_data.get("username")
        if new_username and new_username != self.instance.username:
            current_password = cleaned_data.get("current_password")
            if not current_password or not self.instance.check_password(current_password):
                raise ValidationError("아이디를 변경하려면 현재 비밀번호를 올바르게 입력해야 합니다.")
        return cleaned_data

    def clean_profile_image(self):
        image = self.cleaned_data.get("profile_image")
        if image and hasattr(image, "content_type"):
            if image.content_type not in ALLOWED_IMAGE_TYPES:
                raise ValidationError("jpg, png, webp 형식의 이미지만 업로드할 수 있습니다.")
            if image.size > MAX_IMAGE_SIZE:
                raise ValidationError("이미지 크기는 5MB 이하여야 합니다.")
        return image


class TransferForm(forms.Form):
    amount = forms.IntegerField(min_value=1, max_value=10_000_000, label="송금액")

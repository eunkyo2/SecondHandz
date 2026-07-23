from django import forms
from django.core.exceptions import ValidationError

from accounts.forms import ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE

from .models import Report


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ("target_type", "target_id", "reason", "evidence_image")
        widgets = {"target_type": forms.HiddenInput(), "target_id": forms.HiddenInput()}
        labels = {"evidence_image": "증거 사진(선택)"}

    def clean_evidence_image(self):
        image = self.cleaned_data.get("evidence_image")
        if image and hasattr(image, "content_type"):
            if image.content_type not in ALLOWED_IMAGE_TYPES:
                raise ValidationError("jpg, png, webp 형식의 이미지만 업로드할 수 있습니다.")
            if image.size > MAX_IMAGE_SIZE:
                raise ValidationError("이미지 크기는 5MB 이하여야 합니다.")
        return image

from django import forms

from .models import Product

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("title", "description", "price", "image")

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image:
            if image.content_type not in ALLOWED_IMAGE_TYPES:
                raise forms.ValidationError("jpg, png, webp 형식의 이미지만 업로드할 수 있습니다.")
            if image.size > MAX_IMAGE_SIZE:
                raise forms.ValidationError("이미지 크기는 5MB 이하여야 합니다.")
        return image

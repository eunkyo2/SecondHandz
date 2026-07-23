from django.conf import settings
from django.db import models


class Product(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products")
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=2000)
    price = models.PositiveIntegerField()
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    is_blocked = models.BooleanField(default=False)
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

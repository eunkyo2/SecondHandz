from django.conf import settings
from django.db import models


class Report(models.Model):
    TARGET_CHOICES = [("user", "user"), ("product", "product")]
    STATUS_CHOICES = [("pending", "pending"), ("resolved", "resolved")]

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports_made")
    target_type = models.CharField(max_length=10, choices=TARGET_CHOICES)
    target_id = models.PositiveIntegerField()
    reason = models.CharField(max_length=500)
    evidence_image = models.ImageField(upload_to="reports/", blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

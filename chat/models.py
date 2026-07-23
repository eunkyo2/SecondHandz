from django.conf import settings
from django.db import models

from products.models import Product


class ChatRoom(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="chat_rooms")
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="buying_rooms")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("product", "buyer")

    def is_participant(self, user_id):
        return user_id in (self.buyer_id, self.product.seller_id)

    def other_user(self, current_user):
        return self.product.seller if current_user.id == self.buyer_id else self.buyer


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


class GlobalMessage(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

from django.contrib import admin

from .models import ChatRoom, GlobalMessage, Message

admin.site.register(ChatRoom)
admin.site.register(Message)
admin.site.register(GlobalMessage)

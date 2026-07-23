from django.urls import path

from . import views

urlpatterns = [
    path("", views.room_list, name="chat_list"),
    path("global/", views.global_chat, name="chat_global"),
    path("start/<int:product_id>/", views.start_chat, name="chat_start"),
    path("room/<int:room_id>/", views.room, name="chat_room"),
]

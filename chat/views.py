from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from products.models import Product

from .models import ChatRoom, GlobalMessage


@login_required
def start_chat(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_blocked=False)
    if request.user == product.seller:
        raise PermissionDenied
    room, _ = ChatRoom.objects.get_or_create(product=product, buyer=request.user)
    return redirect("chat_room", room_id=room.pk)


@login_required
def room_list(request):
    rooms = (
        ChatRoom.objects.filter(Q(buyer=request.user) | Q(product__seller=request.user))
        .select_related("product", "buyer", "product__seller")
        .order_by("-created_at")
    )
    room_items = [
        {"room": r, "other": r.other_user(request.user), "last_message": r.messages.order_by("-created_at").first()}
        for r in rooms
    ]
    return render(request, "chat/list.html", {"room_items": room_items})


@login_required
def global_chat(request):
    return render(request, "chat/global.html", {
        "messages_history": GlobalMessage.objects.select_related("sender").order_by("-created_at")[:50][::-1],
    })


@login_required
def room(request, room_id):
    chat_room = get_object_or_404(ChatRoom, pk=room_id)
    if not chat_room.is_participant(request.user.id):
        raise PermissionDenied
    return render(request, "chat/room.html", {
        "room": chat_room,
        "chat_messages": chat_room.messages.select_related("sender"),
    })

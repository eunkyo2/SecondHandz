from django.urls import path

from . import views

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("new/", views.product_create, name="product_create"),
    path("blocked/", views.blocked_list, name="product_blocked_list"),
    path("blocked/<int:pk>/unblock/", views.product_unblock, name="product_unblock"),
    path("<int:pk>/", views.product_detail, name="product_detail"),
    path("<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("<int:pk>/toggle-sold/", views.toggle_sold, name="product_toggle_sold"),
    path("<int:pk>/buy/", views.buy, name="buy"),
]

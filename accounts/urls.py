from django.urls import path

from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.AccountLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dormant/", views.dormant_list, name="dormant_list"),
    path("dormant/<int:pk>/restore/", views.dormant_restore, name="dormant_restore"),
    path("<str:username>/password/", views.change_password, name="change_password"),
    path("<str:username>/transfer/", views.transfer, name="transfer"),
    path("<str:username>/", views.profile, name="profile"),
]

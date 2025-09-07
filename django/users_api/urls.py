from django.urls import path
from . import views

urlpatterns = [
    path("signup", views.signup, name="signup"),
    path("users/<int:user_id>", views.user_detail_view, name="user-detail"),
]

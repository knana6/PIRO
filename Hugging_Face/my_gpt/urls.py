from django.urls import path
from .views import main, chat

urlpatterns = [
    path("", main, name="main"),
    path("api/chat/", chat, name="chat"),
]
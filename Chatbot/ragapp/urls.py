#ragapp/urls.py

from django.urls import path
from .views import ask, ping

urlpatterns = [
path("ask", ask, name="ask"),
path("ping", ping),
]
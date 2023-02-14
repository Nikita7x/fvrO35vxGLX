# urls.py
from django.urls import path
from .views import SlackEvent

from django.urls import path, include

urlpatterns = [
    path('', SlackEvent.as_view()),
]

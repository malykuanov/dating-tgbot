from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import TelegramBotWebhookView

urlpatterns = [
    path('webhook/tgbot', csrf_exempt(TelegramBotWebhookView.as_view())),
]

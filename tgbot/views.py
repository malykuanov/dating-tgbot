import json
import requests

from django.conf import settings
from django.http import JsonResponse
from django.views import View


class TelegramBotWebhookView(View):

    def post(self, request, *args, **kwargs):
        t_data = json.loads(request.body)
        chat_id = t_data["message"]["chat"]["id"]
        TelegramBotWebhookView.send_message(chat_id, "Bye")
        return JsonResponse({"ok": "POST request processed"})

    @staticmethod
    def send_message(chat_id, message):
        url = f"{settings.TELEGRAM_URL}{settings.TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }
        response = requests.post(url, data=data)

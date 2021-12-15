from telebot import types

from django.conf import settings
from django.http import JsonResponse
from django.views import View

from .handlers import bot

bot.remove_webhook()
bot.set_webhook(url=f"{settings.TELEGRAM_WEBHOOK_URL}/webhook/tgbot")


class TelegramBotWebhookView(View):

    def post(self, request, *args, **kwargs):
        json_str = request.body.decode('UTF-8')
        update = types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return JsonResponse({"ok": "POST request processed"})

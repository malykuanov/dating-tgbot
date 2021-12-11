import logging

import telebot
from telebot import types

from django.conf import settings

from .models import User, Profile

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)


@bot.message_handler(commands=['start'])
def start_message(message):
    # User написал /start в диалоге с ботом
    sticker = open('tgbot/static/tgbot/images/welcome.webp', 'rb')
    bot.send_sticker(message.chat.id, sticker)
    try:
        user, created = User.objects.get_or_create(chat_id=message.chat.id)
        if created:
            user.first_name = message.chat.first_name
            user.username = message.chat.username
            user.save()
            profile = Profile.objects.create(user=user)
            logging.info("Create User = ", user)
            text = '<b>Настройка бота!</b>\n\n'
            text += 'Чтобы начать использовать бота, необходимо завести анкету.\n\n'
            text += '......................'

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton(text="❤️Регистрация пользователя")
            markup.add(item1)

            bot.send_message(message.chat.id, text=text, reply_markup=markup,
                             parse_mode='HTML')
    except Exception as ex:
        logging.error(str(ex))

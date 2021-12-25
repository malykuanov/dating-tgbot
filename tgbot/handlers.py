import os
from difflib import SequenceMatcher
import logging

import telebot
from telebot import types

from django.conf import settings

from .models import City, Profile, ProfileSearch, User

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)


def gen_markup_for_city(name):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    cities = City.objects.all()
    for city in cities:
        if SequenceMatcher(None, name, city.name).ratio() > 0.8:
            markup.add(types.InlineKeyboardButton(
                f"{city.name}, {city.region}",
                callback_data=f"city_{city.pk}"
            ))
    markup.add(types.InlineKeyboardButton(
        f"🤷🏻‍♂️Моего города нет в списке",
        callback_data="city_empty"
    ))
    markup.add(types.InlineKeyboardButton(
        f"🙆🏻 Ошибка при вводе",
        callback_data="city_mistake"
    ))
    return markup


def gen_markup_for_profile():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        types.InlineKeyboardButton(
            f"👤Имя",
            callback_data="profile_edit_name"
        ),
        types.InlineKeyboardButton(
            f"🔢Возраст",
            callback_data="profile_edit_age"
        )
    )
    markup.add(
        types.InlineKeyboardButton(
            f"🚹Пол",
            callback_data="profile_edit_sex"
        ),
        types.InlineKeyboardButton(
            f"🏠Город",
            callback_data="profile_edit_city"
        )
    )
    markup.add(
        types.InlineKeyboardButton(
            f"🖌️Описание",
            callback_data="profile_edit_description"
        ),
        types.InlineKeyboardButton(
            f"🖼Фото",
            callback_data="profile_edit_avatar"
        )
    )
    markup.add(
        types.InlineKeyboardButton(
            f"🚫Удаление профиля",
            callback_data="profile_edit_remove"
        )
    )
    return markup


def gen_main_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row_width = 2
    markup.add(
        types.KeyboardButton(f"🔍Поиск"),
        types.KeyboardButton(f"⚙Настройки поиска")
    )
    markup.add(
        types.KeyboardButton(f"😎Мой профиль")
    )

    return markup


def get_user_avatar(user):
    user_avatar = bot.download_file(user.profile.avatar)
    save_path = os.path.join(settings.MEDIA_ROOT, 'images/avatars/')
    file_name = f"{user.chat_id}.jpg"
    complete_name = os.path.join(save_path, file_name)

    with open(complete_name, "wb") as img:
        img.write(user_avatar)
    with open(complete_name, "rb") as img:
        avatar = img.read()
        if os.path.isfile(complete_name):
            os.remove(complete_name)
        return avatar


def get_user_profile(user):
    text = f'<b>👤Имя: </b>{user.profile.name}\n'
    text += f'<b>🔢Возраст: </b>{user.profile.age}\n'
    if user.profile.sex == 'M':
        text += f'<b>🚹Пол: </b> Мужчина\n'
    else:
        text += f'<b>🚺Пол: </b> Женщина\n'
    if user.profile.city is None:
        text += f'<b>🏠Город: </b>Не установлен\n'
    else:
        text += f'<b>🏠Город: </b>{user.profile.city}\n'
    text += f'<b>🖌️Описание: </b>{user.profile.description}\n'

    bot.send_photo(
        chat_id=user.chat_id,
        photo=get_user_avatar(user),
        caption=text,
        parse_mode='HTML'
    )


def get_user_profile_search(user):
    text = f'<i>Ваши настроки для поиска собеседника</i>: \n\n'
    text += f'<b>🔢Возраст: </b>{user.profilesearch.age}\n'
    if user.profilesearch.sex == 'M':
        text += f'<b>🚹Пол: </b> Мужчина\n'
    else:
        text += f'<b>🚺Пол: </b> Женщина\n'
    if user.profile.city is None:
        text += f'<b>🏠Город: </b>Не установлен\n'
    else:
        text += f'<b>🏠Город: </b>{user.profilesearch.city}\n\n'
    text += 'Вы можете изменить настройки поиска: '

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        f"Изменить возраст",
        callback_data="search_age"
    ))
    markup.add(types.InlineKeyboardButton(
        f"Изменить пол",
        callback_data="search_sex"
    ))
    markup.add(types.InlineKeyboardButton(
        f"Изменить город",
        callback_data="search_city"
    ))

    bot.send_message(
        chat_id=user.chat_id,
        text=text,
        reply_markup=markup,
        parse_mode='HTML'
    )


@bot.message_handler(commands=['test'])
def test_command(message):
    pass


@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        sticker_path = os.path.join(
            settings.STATIC_ROOT, 'tgbot/images/welcome.webp'
        )
        with open(sticker_path, 'rb') as sticker:
            bot.send_sticker(message.chat.id, sticker.read())
        user, created = User.objects.get_or_create(chat_id=message.chat.id)
        if created or not user.profile.is_registered:
            user.first_name = message.chat.first_name
            user.username = message.chat.username
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile_search, _ = ProfileSearch.objects.get_or_create(user=user)
            text = '<b>Приветик☺</b>\n\n'
            text += 'Чтобы начать знакомства, необходимо завести анкету.\n'

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(
                f"❤️Регистрация анкеты",
                callback_data="profile_registration"
            ))

            bot.send_message(
                chat_id=message.chat.id,
                text=text,
                reply_markup=markup,
                parse_mode='HTML'
            )
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text="Ку-ку🙂",
                reply_markup=gen_main_markup(),
                parse_mode='HTML'
            )
    except Exception as ex:
        logging.error(str(ex))


@bot.message_handler(commands=['profile'])
def show_user_profile(message):
    try:
        user = User.objects.get(chat_id=message.chat.id)
        if user.profile.is_registered:
            get_user_profile(user)
            bot.send_message(
                chat_id=message.chat.id,
                text="Вы можете изменить параметры профиля:",
                reply_markup=gen_markup_for_profile(),
                parse_mode='HTML'
            )
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text="Вы не завершили регистрацию!\nВоспользуйтесь командой:\n/start"
            )
    except User.DoesNotExist as ex:
        bot.send_message(
            chat_id=message.chat.id,
            text="Вы не завели анкету!\nВоспользуйтесь командой:\n/start"
        )
    except Exception as ex:
        logging.error(ex)


@bot.message_handler(commands=['bug'])
def delete_profile(message):
    text = '<b>Отправьте сообщение об ошибке администратору бота</b>\n'
    text += 'Укажите в какой момент времени и какая ошибка возникла'
    message = bot.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode='HTML'
    )
    bot.register_next_step_handler(message, process_bug_step)


@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.chat.type == 'private':
        if message.text == '😎Мой профиль':
            show_user_profile(message)
        if message.text == '⚙Настройки поиска':
            user = User.objects.get(chat_id=message.chat.id)
            get_user_profile_search(user)


def process_name_step(message, user):
    try:
        name = message.text
        if len(name) > 20:
            bot.reply_to(
                message=message,
                text='Ваше имя слишком длинное, используйте до 20 сим.'
            )
            bot.register_next_step_handler(message, process_name_step, user)
            return
        user.profile.name = name
        user.profile.save()
        bot.send_message(chat_id=message.chat.id, text='Имя установлено!')
        if user.profile.is_registered:
            show_user_profile(message)
        else:
            message = bot.reply_to(message, 'Сколько вам лет?')
            bot.register_next_step_handler(message, process_age_step, user)
    except Exception as ex:
        logging.error(ex)


def process_age_step(message, user):
    try:
        age = message.text
        if not age.isdigit() or not 18 <= int(age) <= 100:
            message = bot.reply_to(
                message=message,
                text='Укажите возраст цифрами от 18 до 100'
            )
            bot.register_next_step_handler(message, process_age_step, user)
            return
        user.profile.age = age
        user.profile.save()
        bot.send_message(chat_id=message.chat.id, text='Возраст установлен!')
        if user.profile.is_registered:
            show_user_profile(message)
        else:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                               resize_keyboard=True)
            markup.add('Мужчина', 'Женщина')
            message = bot.reply_to(message, 'Укажите ваш пол',
                                   reply_markup=markup)
            bot.register_next_step_handler(message, process_sex_step, user)
    except Exception as ex:
        logging.error(ex)


def process_sex_step(message, user):
    try:
        sex = message.text
        if sex == 'Мужчина':
            user.profile.sex = 'M'
            user.profilesearch.sex = 'F'
        elif sex == 'Женщина':
            user.profile.sex = 'F'
            user.profilesearch.sex = 'M'
        else:
            message = bot.reply_to(
                message=message,
                text='Выберите пол из предложенных вариантов (Мужчина / Женщина)'
            )
            bot.register_next_step_handler(message, process_sex_step, user)
            return
        user.profile.save()
        user.profilesearch.save()
        bot.send_message(chat_id=message.chat.id, text='Пол установлен!')
        if user.profile.is_registered:
            show_user_profile(message)
        else:
            message = bot.send_message(
                chat_id=message.chat.id,
                text='Укажите ваш город',
                reply_markup=types.ReplyKeyboardRemove()
            )
            bot.register_next_step_handler(message, process_city_step, user)
    except Exception as ex:
        logging.error(ex)


def process_city_step(message, user):
    try:
        city = message.text
        text = '<b>Выберите населенный пункт:</b>\n'
        text += '(в списке предложены н/п с численностью <u>более 1000 ч.</u>)\n\n'
        text += 'Если вашего н/п нет в списке, выберите пункт:\n'
        text += '<i>`Моего н/п нет в списке`</i>'
        bot.send_message(
            chat_id=message.chat.id,
            text=text,
            reply_markup=gen_markup_for_city(city),
            parse_mode='HTML'
        )
    except Exception as ex:
        logging.error(ex)


def process_description_step(message, user):
    try:
        description = message.text
        if len(description) > 400:
            message = bot.reply_to(
                message=message,
                text='Слишком длинное описание, до 400 сим.'
            )
            bot.register_next_step_handler(message, process_description_step,
                                           user)
            return
        user.profile.description = description
        user.profile.save()
        bot.send_message(chat_id=message.chat.id, text='Описание установлено!')
        if user.profile.is_registered:
            show_user_profile(message)
        else:
            message = bot.reply_to(message, 'Пришлите ваше фото')
            bot.register_next_step_handler(message, process_photo_step, user)
    except Exception as ex:
        logging.error(ex)


def process_photo_step(message, user):
    try:
        file_id = message.photo[-1].file_id
        file = bot.get_file(file_id)
        user.profile.avatar = file.file_path
        user.profile.save()
        bot.send_message(chat_id=message.chat.id, text='Фото установлено!')
        if user.profile.is_registered:
            show_user_profile(message)
        else:
            user.profile.is_registered = True
            user.profile.save()
            text = '<b>Поздравляем!!!</b> Ваша анкета успешно создана\n'
            text += 'Для просмотра текущего профиля укажите команду\n'
            text += '/profile или воспользуйтесь кнопкой "Мой профиль"'
            bot.send_message(
                chat_id=message.chat.id,
                text=text,
                reply_markup=gen_main_markup(),
                parse_mode='HTML'
            )
    except TypeError:
        message = bot.reply_to(
            message=message,
            text='Поддерживаемый формат: PNG/JPG\n(compress/сжатое)'
        )
        bot.register_next_step_handler(message, process_photo_step, user)
    except Exception as ex:
        logging.error(ex)


def process_bug_step(message):
    try:
        bug = message.text
        text = '<b>Спасибо за информацию👍</b>\n'
        text += 'Наша команда проверит информацию и свяжется с вами!'
        bot.reply_to(
            message=message,
            text=text,
            parse_mode='HTML'
        )

        logging.warning(f'BUG from {message.chat.id}: {bug}')
    except Exception as ex:
        logging.error(ex)


@bot.callback_query_handler(func=lambda call: call.data.startswith('city_'))
def callback_set_city(call):
    try:
        bot.edit_message_reply_markup(call.from_user.id,
                                      call.message.message_id)

        user = User.objects.get(chat_id=call.from_user.id)
        text = ""
        if call.data == 'city_empty':
            text = 'После регистрации <b>свяжитесь с администратором бота</b>\n'
            text += 'Для этого воспользутей командой /bug и сообщите о проблеме'
        elif call.data == 'city_mistake':
            text = 'Упс, бывает ...'
            bot.edit_message_text(
                chat_id=call.from_user.id,
                message_id=call.message.message_id,
                text=text,
                parse_mode='HTML'
            )
            message = bot.send_message(call.from_user.id,
                                       'Укажите ваш город')
            bot.register_next_step_handler(message, process_city_step, user)
            return
        else:
            city_pk = call.data.split('_')[-1]
            user.profile.city = City.objects.get(pk=city_pk)
            user.profilesearch.city = user.profile.city
            user.profilesearch.save()
            user.profile.save()
            text = '<b>Город установлен</b>\n'
            if user.profile.is_registered:
                show_user_profile(call.message)
        bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text=text,
            parse_mode='HTML'
        )
        bot.answer_callback_query(call.id)

        if not user.profile.is_registered:
            message = bot.send_message(
                chat_id=call.from_user.id,
                text='Укажите описание о себе до 400 сим.'
            )
            bot.register_next_step_handler(message, process_description_step,
                                           user)

    except Exception as ex:
        logging.error(ex)


@bot.callback_query_handler(func=lambda call: call.data.startswith('profile_'))
def callback_change_profile(call):
    try:
        bot.edit_message_reply_markup(
            chat_id=call.from_user.id,
            message_id=call.message.message_id
        )
        text = ""
        user = User.objects.get(chat_id=call.from_user.id)

        if call.data == 'profile_registration':
            bot.send_message(
                chat_id=call.from_user.id,
                text="Как вас зовут?"
            )
            bot.register_next_step_handler(call.message, process_name_step,
                                           user)
            bot.answer_callback_query(call.id)
            return

        if call.data == 'profile_edit_name':
            bot.send_message(
                chat_id=call.from_user.id,
                text="Укажите ваше имя:"
            )
            bot.register_next_step_handler(call.message, process_name_step,
                                           user)
            bot.answer_callback_query(call.id)
            return
        if call.data == 'profile_edit_age':
            bot.send_message(
                chat_id=call.from_user.id,
                text="Укажите ваш возраст:"
            )
            bot.register_next_step_handler(call.message, process_age_step,
                                           user)
            bot.answer_callback_query(call.id)
            return
        if call.data == 'profile_edit_sex':
            bot.send_message(
                chat_id=call.from_user.id,
                text="Укажите ваш пол (Мужчина / Женщина):"
            )
            bot.register_next_step_handler(call.message, process_sex_step,
                                           user)
            bot.answer_callback_query(call.id)
            return
        if call.data == 'profile_edit_city':
            bot.send_message(
                chat_id=call.from_user.id,
                text="Укажите ваш город:"
            )
            bot.register_next_step_handler(call.message, process_city_step,
                                           user)
            bot.answer_callback_query(call.id)
            return
        if call.data == 'profile_edit_description':
            bot.send_message(
                chat_id=call.from_user.id,
                text="Укажите описание:"
            )
            bot.register_next_step_handler(call.message,
                                           process_description_step,
                                           user)
            bot.answer_callback_query(call.id)
            return
        if call.data == 'profile_edit_avatar':
            bot.send_message(
                chat_id=call.from_user.id,
                text="Пришлите ваше фото:"
            )
            bot.register_next_step_handler(call.message, process_photo_step,
                                           user)
            bot.answer_callback_query(call.id)
            return
        if call.data == 'profile_edit_remove':
            text = '<b>Вы точно хотите удалить анкету❓</b>\n'
            markup = types.InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(types.InlineKeyboardButton(
                text="❌Удалить анкету",
                callback_data="profile_delete"
            ))
            markup.add(types.InlineKeyboardButton(
                text="☺Я остаюсь!",
                callback_data="profile_save"
            ))
            bot.send_message(
                chat_id=call.message.chat.id,
                text=text,
                reply_markup=markup,
                parse_mode='HTML'
            )
            bot.answer_callback_query(call.id)
            return
        if call.data == 'profile_save':
            text = "Ура😌"
        elif call.data == 'profile_delete':
            text = "Ваша анкета успешно удалена!\n"
            text += "Для создания новой анкеты: /start"
            user.delete()

        bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text=text
        )
        bot.answer_callback_query(call.id)

    except User.DoesNotExist:
        bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text="Вы не завели анкету!\nВоспользуйтесь командой:\n/start"
        )
    except Exception as ex:
        logging.error(ex)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    pass

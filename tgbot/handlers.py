import functools
import os
from difflib import SequenceMatcher
import logging

import telebot
from telebot import types

from django.conf import settings

from .models import City, Profile, ProfileSearch, User

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logger.exception(
                f"Exception raised in {func.__name__}. exception: {str(e)}")
            raise e

    return wrapper


@log
def gen_markup_for_city(name, is_search):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    cities = City.objects.all()
    for city in cities:
        if SequenceMatcher(None, name, city.name).ratio() > 0.8:
            callback = 'search_' if is_search else ''
            markup.add(types.InlineKeyboardButton(
                f"{city.name}, {city.region}",
                callback_data=f"city_{callback}{city.pk}"
            ))
    markup.add(types.InlineKeyboardButton(
        f"🤷🏻‍♂️Города нет в списке",
        callback_data="city_empty"
    ))
    return markup


@log
def gen_markup_for_profile(user):
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
    if user.profile.is_active:
        text_active = '✅Анкета активна'
    else:
        text_active = '⛔Анкета не активна'
    markup.add(
        types.InlineKeyboardButton(
            text=text_active,
            callback_data="profile_edit_active"
        )
    )
    return markup


@log
def gen_markup_for_profile_search():
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

    return markup


@log
def gen_markup_for_age_search():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    age_range = [age for age in range(13, 55, 5)]
    for index in range(0, 8, 2):
        first_diapason = f'{age_range[index]}-{age_range[index + 1]}'
        second_diapason = f'{age_range[index + 1]}-{age_range[index + 2]}'
        markup.add(
            types.InlineKeyboardButton(
                text=first_diapason,
                callback_data=f'search_age_{first_diapason}'
            ),
            types.InlineKeyboardButton(
                text=second_diapason,
                callback_data=f'search_age_{second_diapason}'
            )
        )
    markup.add(
        types.InlineKeyboardButton(
            text=f'50-100',
            callback_data=f'search_age_50-100'
        ),
        types.InlineKeyboardButton(
            text='Любой возраст',
            callback_data=f'search_age_13-100'
        )
    )
    return markup


@log
def gen_markup_for_sex_search():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        types.InlineKeyboardButton(
            text=f'🕺🏻',
            callback_data=f'search_sex_M'
        ),
        types.InlineKeyboardButton(
            text='💃🏻',
            callback_data=f'search_sex_F'
        )
    )
    return markup


@log
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


@log
def get_user_avatar(user):
    save_path = os.path.join(settings.MEDIA_ROOT, 'images/avatars/')
    file_name = f"{user.chat_id}.jpg"
    complete_name = os.path.join(save_path, file_name)

    with open(complete_name, "rb") as img:
        avatar = img.read()
        return avatar


@log
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
    text += f'<b>🖌️Описание: </b>{user.profile.description}\n\n'
    text += '<i>Так выглядит ваш профиль</i>\n'
    text += 'Вы можете изменить следующие параметры:'
    bot.send_photo(
        chat_id=user.chat_id,
        photo=get_user_avatar(user),
        caption=text,
        reply_markup=gen_markup_for_profile(user),
        parse_mode='HTML'
    )


@log
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

    return text


@log
def get_next_search_profile(client):
    try:
        user_id = client.profilesearch.unviewed.pop()
        user = User.objects.get(chat_id=user_id)
        text = f'<b>{user.profile.name}, </b>'
        text += f'{user.profile.age}, '
        text += f'{user.profile.city.name}\n'
        text += f'<i>{user.profile.description}</i>'
        markup = types.InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(
            types.InlineKeyboardButton(
                text='💌 Написать',
                url=f'tg://user?id={user.chat_id}'
            )
        )
        bot.send_photo(
            chat_id=client.chat_id,
            photo=get_user_avatar(user),
            caption=text,
            reply_markup=markup,
            parse_mode='HTML'
        )
        client.profilesearch.viewed.append(user_id)
        client.profilesearch.save()
    except IndexError:
        text = 'К сожалению, мы никого <b>не нашли</b>\n'
        text += 'Попробуйте изменить настройки поиска'
        bot.send_message(
            chat_id=client.chat_id,
            text=text,
            parse_mode='HTML'
        )


@bot.message_handler(commands=['start'])
@log
def start_message(message):
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


@bot.message_handler(commands=['profile'])
@log
def show_user_profile(message):
    try:
        user = User.objects.get(chat_id=message.chat.id)
        if user.profile.is_registered:
            get_user_profile(user)
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


@bot.message_handler(commands=['bug'])
@log
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
@log
def bot_message(message):
    if message.chat.type == 'private':
        if message.text == '😎Мой профиль':
            show_user_profile(message)
        if message.text == '⚙Настройки поиска':
            user = User.objects.get(chat_id=message.chat.id)
            bot.send_message(
                chat_id=user.chat_id,
                text=get_user_profile_search(user),
                reply_markup=gen_markup_for_profile_search(),
                parse_mode='HTML'
            )
        if message.text == '🔍Поиск':
            client = User.objects.get(chat_id=message.chat.id)
            if not client.profilesearch.unviewed:
                start_age, end_age = map(
                    int,
                    client.profilesearch.age.split('-')
                )
                list_users_for_search = User.objects.filter(
                    profile__age__range=(start_age, end_age),
                    profile__sex=client.profilesearch.sex,
                    profile__city=client.profilesearch.city
                ).exclude(chat_id=client.chat_id).order_by('?')

                for user in list_users_for_search:
                    if (user.chat_id not in client.profilesearch.viewed and
                            user.chat_id not in client.profilesearch.unviewed):
                        client.profilesearch.unviewed.append(user.chat_id)
                client.profilesearch.save()

            get_next_search_profile(client)


@log
def process_name_step(message, user):
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


@log
def process_age_step(message, user):
    age = message.text
    if not age.isdigit() or not 13 <= int(age) <= 100:
        message = bot.reply_to(
            message=message,
            text='Укажите возраст цифрами от 13 до 100'
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


@log
def process_sex_step(message, user):
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
    if user.profile.is_registered:
        bot.send_message(
            chat_id=message.chat.id,
            text='Пол установлен!',
            reply_markup=gen_main_markup()
        )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text='Пол установлен!',
            reply_markup=types.ReplyKeyboardRemove()
        )
        message = bot.send_message(
            chat_id=message.chat.id,
            text='Укажите ваш город',
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, process_city_step)


@log
def process_city_step(message, is_search=False):
    city = message.text
    text = '<b>Выберите населенный пункт:</b>\n'
    text += '(в списке предложены н/п с численностью <u>более 1000 ч.</u>)\n\n'
    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=gen_markup_for_city(city, is_search),
        parse_mode='HTML'
    )


@log
def process_description_step(message, user):
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


@log
def process_photo_step(message, user):
    try:
        file_id = message.photo[-1].file_id
        file = bot.get_file(file_id)
        user_avatar = bot.download_file(file.file_path)
        save_path = os.path.join(settings.MEDIA_ROOT, 'images/avatars/')
        file_name = f"{user.chat_id}.jpg"
        complete_name = os.path.join(save_path, file_name)

        with open(complete_name, "wb") as img:
            img.write(user_avatar)

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


@log
def process_bug_step(message):
    bug = message.text
    text = '<b>Спасибо за информацию👍</b>\n'
    text += 'Наша команда проверит информацию и свяжется с вами!'
    bot.reply_to(
        message=message,
        text=text,
        parse_mode='HTML'
    )

    logging.warning(f'BUG from {message.chat.id}: {bug}')


@bot.callback_query_handler(func=lambda call: call.data.startswith('city_'))
@log
def callback_set_city(call):
    bot.edit_message_reply_markup(call.from_user.id,
                                  call.message.message_id)

    user = User.objects.get(chat_id=call.from_user.id)
    text = ""

    if call.data == 'city_empty':
        text = 'Пожалуйста, <b>свяжитесь с администратором бота</b>\n'
        text += 'Для этого воспользутей командой /bug и сообщите о проблеме'
        if user.profile.city is None:
            user.profile.city = City.objects.get(
                name='Город не установлен')
            user.profilesearch.city = user.profile.city
    else:
        city_pk = call.data.split('_')[-1]
        if call.data.startswith('city_search'):
            user.profilesearch.city = City.objects.get(pk=city_pk)
            user.profilesearch.unviewed.clear()
            text = '<b>Город собеседника установлен</b>\n'
        else:
            user.profile.city = City.objects.get(pk=city_pk)
            user.profilesearch.city = user.profile.city
            text = '<b>Город установлен</b>\n'

    user.profile.save()
    user.profilesearch.save()

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
        bot.register_next_step_handler(message, process_description_step, user)


@bot.callback_query_handler(func=lambda call: call.data.startswith('profile_'))
@log
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
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                               resize_keyboard=True)
            markup.add('Мужчина', 'Женщина')
            bot.send_message(
                chat_id=call.from_user.id,
                text="Укажите ваш пол:",
                reply_markup=markup
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
            bot.register_next_step_handler(call.message, process_city_step)
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
        if call.data == 'profile_edit_active':
            user.profile.is_active = not user.profile.is_active
            user.profile.save()
            show_user_profile(call.message)
            bot.answer_callback_query(call.id, 'Статус анкеты изменен')
            return

    except User.DoesNotExist:
        bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text="Вы не завели анкету!\nВоспользуйтесь командой:\n/start"
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith('search_'))
@log
def callback_change_profile_search(call):
    try:
        user = User.objects.get(chat_id=call.from_user.id)
        text = markup = None

        if call.data == 'search_age':
            text = '<b>Выберите возрастной диапозон</b>: '
            markup = gen_markup_for_age_search()
            bot.answer_callback_query(call.id)
        if call.data.startswith('search_age_'):
            user.profilesearch.age = call.data.split('_')[-1]
            user.profilesearch.unviewed.clear()
            user.profilesearch.save()
            text = get_user_profile_search(user)
            markup = gen_markup_for_profile_search()

        if call.data == 'search_sex':
            text = 'Выберите пол собеседника'
            markup = gen_markup_for_sex_search()
        if call.data.startswith('search_sex_'):
            user.profilesearch.sex = call.data.split('_')[-1]
            user.profilesearch.unviewed.clear()
            user.profilesearch.save()
            text = get_user_profile_search(user)
            markup = gen_markup_for_profile_search()

        if call.data == 'search_city':
            bot.delete_message(
                chat_id=call.from_user.id,
                message_id=call.message.message_id
            )
            bot.send_message(
                chat_id=call.from_user.id,
                text='<b>Укажите город собеседника:</b> ',
                parse_mode='HTML'
            )
            is_search = True
            bot.register_next_step_handler(call.message, process_city_step,
                                           is_search)
            bot.answer_callback_query(call.id)
            return

        bot.edit_message_text(
            text=text,
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            parse_mode='HTML'
        )
        bot.edit_message_reply_markup(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
        return

    except User.DoesNotExist:
        bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text="Вы не завели анкету!\nВоспользуйтесь командой:\n/start"
        )

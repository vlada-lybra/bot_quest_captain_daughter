import json
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_quest_dict(json_path):
    """
    Функция для получения словаря квеста
    """
    with open(json_path, 'r') as file:
        result = json.load(file)
    return result


def get_markup(answers_dict):
    """
    Функция для получения клавиатуры ответов на вопросы квеста
    """
    result = InlineKeyboardMarkup()

    for button_name, button_callback in answers_dict.items():
        result.add(InlineKeyboardButton(button_name, callback_data=button_callback))

    return result


def get_start_markup():
    """
    Функция для получения клавиатуры начала квеста
    """
    result = InlineKeyboardMarkup()

    result.add(InlineKeyboardButton("Начать квест", callback_data='start_quest'))

    return result


def get_finish_markup():
    """
    Функция для получения клавиатуры окончания квеста
    """
    result = InlineKeyboardMarkup()

    result.add(InlineKeyboardButton("Да", callback_data='start_quest'))
    result.add(InlineKeyboardButton("Нет", callback_data='end_quest'))

    return result


def get_user_state(user_id):
    """
    Функция для получения текущего состояния пользователя по id
    """

    # Если файл существует
    try:
        try:
            # Открыть его и вернуть найденное значение
            with open('progress.json', 'r') as file:
                state = json.load(file)
                return state.get(str(user_id))["state"]
        except KeyError:
            return
        except TypeError:
            return

    # Иначе вернуть None
    except FileNotFoundError:
        return


def update_user_state(user_id, position):
    """
    Функция для обновления состояния пользователя
    """

    # Если файл существует
    try:
        # Открыть файл
        with open('progress.json', 'r') as file:
            positions = json.load(file)
        # Обновить состояние у пользователя
        if str(user_id) in positions.keys():
            positions[str(user_id)]["state"] = position
        else:
            positions[str(user_id)] = {}
            positions[str(user_id)]["state"] = position
        # Перезаписать файл
        with open('progress.json', 'w') as file:
            json.dump(positions, file)

    # Иначе
    except FileNotFoundError:
        # Создать файл и сделать в него первую запись
        with open('progress.json', 'w') as file:
            json.dump({str(user_id): {"state": position}}, file)


def get_user_last_message_id(user_id):
    """
    Функция для получения идентификатора последнего сообщения бота пользователю
    """

    # Если файл существует
    try:
        # Открыть его и вернуть найденное значение
        with open('progress.json', 'r') as file:
            ids = json.load(file)
            return ids.get(str(user_id))["id"]

    # Иначе вернуть None
    except FileNotFoundError:
        return


def update_user_last_message_id(user_id, ident):
    """
    Функция для обновления идентификатора последнего сообщения бота пользователю
    """

    # Если файл существует
    try:
        # Открыть файл
        with open('progress.json', 'r') as file:
            ids = json.load(file)
        # Обновить состояние у пользователя
        if str(user_id) in ids.keys():
            ids[str(user_id)]["id"] = ident
        else:
            ids[str(user_id)] = {}
            ids[str(user_id)]["id"] = ident
        # Перезаписать файл
        with open('progress.json', 'w') as file:
            json.dump(ids, file)

    # Иначе
    except FileNotFoundError:
        # Создать файл и сделать в него первую запись
        with open('progress.json', 'w') as file:
            json.dump({str(user_id): {"id": ident}}, file)


def send_message_by_call(bot, call, call_data, dict_path, is_update_user_state):
    """
    Функция для отправки сообщения квеста по полученным данным
    """

    # Получение идентификатора чата
    chat_id = call.message.chat.id

    # Если найдено изображение для локации
    try:
        # Получение пути к изображению
        picture_path = f"{get_quest_dict(dict_path)[call_data]['picture']}.jpg"

        # Если это не финальное сообщение
        try:
            # Отправить сообщение с клавиатурой выбора
            with open(picture_path, 'rb') as photo:
                mes = bot.send_photo(chat_id, photo, get_quest_dict(dict_path)[call_data]['description'],
                                     reply_markup=get_markup(get_quest_dict(dict_path)[call_data]['options']))

            if is_update_user_state:
                update_user_state(chat_id, call_data)

        # Если это финальное сообщение
        except KeyError:
            # Отправить фото без клавиатуры
            with open(picture_path, 'rb') as photo:
                bot.send_photo(chat_id, photo, get_quest_dict(dict_path)[call_data]['description'],
                               reply_markup=None)

            if is_update_user_state:
                update_user_state(chat_id, None)

            mes = bot.send_message(chat_id, "Хотите пройти квеcт еще раз?", reply_markup=get_finish_markup())

    # Если у локации нет изображения
    except KeyError:
        # Если это не финальное сообщение
        try:
            # Отправить сообщение с клавиатурой
            mes = bot.send_message(chat_id, get_quest_dict(dict_path)[call_data]['description'],
                                   reply_markup=get_markup(get_quest_dict(dict_path)[call_data]['options']))

            if is_update_user_state:
                update_user_state(chat_id, call_data)

        # Если это финальное сообщение
        except KeyError:
            # Отправить сообщение без клавиатуры
            bot.send_message(chat_id, get_quest_dict(dict_path)[call_data]['description'], reply_markup=None)

            if is_update_user_state:
                update_user_state(chat_id, None)

            mes = bot.send_message(chat_id, "Хотите пройти квеcт еще раз?", reply_markup=get_finish_markup())
    # Если файл изображения не найден
    except FileNotFoundError:
        # Если это не финальное сообщение
        try:
            # Отправить сообщение с клавиатурой
            mes = bot.send_message(chat_id, get_quest_dict(dict_path)[call_data]['description'],
                                   reply_markup=get_markup(get_quest_dict(dict_path)[call_data]['options']))

            if is_update_user_state:
                update_user_state(chat_id, call_data)

        # Если это финальное сообщение
        except KeyError:
            # Отправить сообщение без клавиатуры
            bot.send_message(chat_id, get_quest_dict(dict_path)[call_data]['description'], reply_markup=None)
            if is_update_user_state:
                update_user_state(chat_id, None)
            mes = bot.send_message(chat_id, "Хотите пройти квеcт еще раз?", reply_markup=get_finish_markup())

    return mes.id

import telebot

from info import get_quest_dict, get_start_markup, get_user_state, get_user_last_message_id, update_user_last_message_id, send_message_by_call

TOKEN = ''

bot = telebot.TeleBot(TOKEN)

# Функция для обработки команды /start
@bot.message_handler(commands=['start'])
def start_command(message):
    try:
        # Получение идентификатора чата
        chat_id = message.chat.id

        # Убирание клавиатуры у предыдущего сообщения, если она есть
        try:
            bot.edit_message_reply_markup(chat_id, get_user_last_message_id(chat_id), reply_markup=None)
        except Exception:
            pass

        # Отправка приветственного сообщения с закрытием клавиатуры, если она открыта
        mes = bot.send_message(chat_id, 'Привет! Этот бот позволяет пройти квест по исторической повести А.С. Пушкина "Капитанская дочка"\n'
                                             'Чтобы узнать, что какие команды есть в чат-боте, напиши /help',
                               reply_markup=get_start_markup()
                               )

        # Обновление идентификатора последнего сообщения бота пользователю
        update_user_last_message_id(chat_id, mes.id)

    except Exception:
        bot.send_message(message.chat.id, 'Что-то пошло не так!', reply_markup=None)

# Функция для обработки команды /help
@bot.message_handler(commands=['help'])
def help_command(message):
     try:
        # Отправка сообщения с командами с закрытием клавиатуры, если она открыта
        bot.send_message(message.chat.id, "Бот поддерживает следующие команды:\n"
                                          "1. /start - приветственное сообщение\n"
                                          "2. /help - узнать возможности бота\n"
                                          "3. Или нажмите на кнопку ниже, чтобы начать квест", reply_markup=get_start_markup())

     except Exception:
        bot.send_message(message.chat.id, 'Что-то пошло не так!', reply_markup=None)

# Обработка команд квеста
@bot.callback_query_handler(func=lambda call: call.data in get_quest_dict('test_dictionary_1.json').keys())
def quest_question(call):
    try:
        # Убирание клавиатуры у предыдущего сообщения, если она есть
        try:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        except Exception:
            pass

        # Получение текущего состояния пользователя
        current_state = get_user_state(call.message.chat.id)

        # Если это сообщение для запуска квеста, но у пользователя есть состояние
        if call.data == 'start_quest' and current_state is not None:
            mes_id = send_message_by_call(bot, call, current_state, 'test_dictionary_1.json', False)

        # Иначе
        else:
            mes_id = send_message_by_call(bot, call, call.data, 'test_dictionary_1.json', True)

        update_user_last_message_id(call.message.chat.id, mes_id)

    except Exception:
        bot.send_message(call.message.chat.id, 'Что-то пошло не так!', reply_markup=None)

# Обработка команды окончания квеста
@bot.callback_query_handler(func=lambda call: call.data == 'end_quest')
def end_quest(call):
    try:
        # Убирание клавиатуры у предыдущего сообщения, если она есть
        try:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        except Exception:
            pass

        bot.send_message(call.message.chat.id, "Конец игры, нажмите /start", reply_markup=None)
    except Exception:
        bot.send_message(call.message.chat.id, 'Что-то пошло не так!', reply_markup=None)

# Обработка неизвестных сообщений
@bot.message_handler()
def unknown_command(message):
    try:
        # Убирание клавиатуры у предыдущего сообщения, если она есть
        try:
            bot.edit_message_reply_markup(message.chat.id, get_user_last_message_id(message.chat.id), reply_markup=None)
        except Exception:
            pass

        bot.send_message(message.chat.id, "Мне неизвестна эта команда. Воспользуйтесь командой /start", reply_markup=None)
    except Exception:
        bot.send_message(message.chat.id, 'Что-то пошло не так!', reply_markup=None)


# Запуск поллинга
bot.polling()
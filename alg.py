import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "7221205358:AAEzSNTzm7dUvis2WCqkplUwLxlc6TDjek8"
bot = telebot.TeleBot(TOKEN)

days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]

# Хранилище для данных пользователей
user_ids = set()  # Множество для хранения ID пользователей

# Главное меню
def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)  # Задаем ширину ряда 2, чтобы кнопки располагались по 2
    keyboard.row(
        InlineKeyboardButton("Четная неделя", callback_data="even_week"),
        InlineKeyboardButton("Нечетная неделя", callback_data="odd_week")
    )
    return keyboard

# Меню для выбора дня недели
def days_menu():
    keyboard = InlineKeyboardMarkup()
    for day in days:
        keyboard.add(InlineKeyboardButton(day, callback_data=f"day_{day}"))
    keyboard.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))
    return keyboard

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_ids.add(message.from_user.id)  # Сохраняем ID пользователя
    bot.send_message(message.chat.id, "Выберите неделю:", reply_markup=main_menu())

# Обработчик нажатия кнопок с выбором недели
@bot.callback_query_handler(func=lambda call: call.data in ["even_week", "odd_week"])
def week_selected(call):
    bot.edit_message_text("Выберите день недели:", call.message.chat.id, call.message.message_id, reply_markup=days_menu())

# Обработчик нажатия кнопок с днями недели
@bot.callback_query_handler(func=lambda call: call.data.startswith("day_"))
def day_selected(call):
    bot.answer_callback_query(call.id, f"Вы выбрали: {call.data[4:]}")

# Обработчик нажатия кнопки "⬅ Назад"
@bot.callback_query_handler(func=lambda call: call.data == "back")
def go_back(call):
    bot.edit_message_text("Выберите неделю:", call.message.chat.id, call.message.message_id, reply_markup=main_menu())

# Обработчик команды /cast для рассылки сообщения всем пользователям
@bot.message_handler(commands=['cast'])
def send_broadcast(message):
    # Проверяем, что сообщение пришло от администратора (замените на свой ID)
    if message.from_user.id == 1077090809:  # Замените на свой ID
        bot.send_message(message.chat.id, "Введите сообщение для рассылки всем пользователям:")
        bot.register_next_step_handler(message, broadcast_message)
    else:
        bot.send_message(message.chat.id, "У вас нет прав для использования этой команды.")

# Функция для рассылки сообщений
def broadcast_message(message):
    text = message.text
    for user_id in user_ids:
        try:
            bot.send_message(user_id, text)
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
    bot.send_message(message.chat.id, "Сообщение отправлено всем пользователям!")

# Обработчик для удаления сообщений, которые не являются командами
@bot.message_handler(func=lambda message: not message.text.startswith('/'))
def delete_non_command_messages(message):
    bot.delete_message(message.chat.id, message.message_id)

if __name__ == "__main__":
    print("Bot started...")
    bot.polling(none_stop=True)
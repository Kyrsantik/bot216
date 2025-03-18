import telebot
import sqlite3
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "7221205358:AAEzSNTzm7dUvis2WCqkplUwLxlc6TDjek8"
bot = telebot.TeleBot(TOKEN)

days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]

user_ids = set()
# Глобальная переменная для хранения текущей базы данных (четная/нечетная неделя)
current_db = "ch.db"  # По умолчанию четная неделя


# Функция получения данных из таблицы по дню недели
def get_schedule_by_day(day):
    table_names = {
        "Понедельник": "Понедельник",
        "Вторник": "Вторник",
        "Среда": "Среда",
        "Четверг": "Четверг",
        "Пятница": "Пятница"
    }
    table_name = table_names.get(day)

    if not table_name:
        return "Ошибка: Таблица не найдена."

    try:
        conn = sqlite3.connect(current_db)  # Подключаемся к текущей базе
        cursor = conn.cursor()

        # Проверяем, существует ли таблица
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
        if not cursor.fetchone():
            conn.close()
            return f"Ошибка: Таблица '{table_name}' не найдена в базе."

        cursor.execute(f"SELECT * FROM {table_name}")  # Запрос всех строк из таблицы
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return "Данные отсутствуют."

        # Формируем строку с расписанием
        schedule = []
        for row in rows:
            if any(field not in ["-", None, ""] for field in row[1:]):
                # Распределяем все элементы строки согласно таблице
                pair_number = row[0]  # Первый столбец - номер пары
                subject = row[1]  # Второй столбец - название пары
                teacher = row[2]  # Третий столбец - учитель
                classroom = row[3]  # Четвертый столбец - кабинет

                # Формируем запись с номером пары и остальными данными
                schedule_entry = (
                    f"┌ {pair_number} пара\n"
                    f"├ {subject}\n"
                    f"├ {teacher}\n"
                    f"└ {classroom}\n"
                )
                schedule.append(schedule_entry)

        return f"📅 Расписание на {day}:\n\n" + "\n".join(schedule) if schedule else "Пар нет."

    except Exception as e:
        return f"Ошибка при получении данных: {e}"


# Главное меню
def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.row(
        InlineKeyboardButton("Четная неделя", callback_data="even_week"),
        InlineKeyboardButton("Нечетная неделя", callback_data="odd_week")
    )
    return keyboard


# Меню для выбора дня недели
def days_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)  # Дни будут отображаться по 2 в ряд
    for day in days:
        keyboard.add(InlineKeyboardButton(day, callback_data=f"day_{day}"))
    keyboard.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))
    return keyboard


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Выберите неделю:", reply_markup=main_menu())


# Обработчик выбора недели (меняет базу данных)
@bot.callback_query_handler(func=lambda call: call.data in ["even_week", "odd_week"])
def week_selected(call):
    global current_db
    if call.data == "even_week":
        current_db = "ch.db"  # Четная неделя
    else:
        current_db = "nech.db"  # Нечетная неделя

    try:
        bot.edit_message_text("Выберите день недели:", call.message.chat.id, call.message.message_id,
                              reply_markup=days_menu())
    except telebot.apihelper.ApiException:
        bot.send_message(call.message.chat.id, "Выберите день недели:", reply_markup=days_menu())


# Обработчик выбора дня недели
@bot.callback_query_handler(func=lambda call: call.data.startswith("day_"))
def day_selected(call):
    day = call.data[4:]  # Извлекаем название дня
    schedule = get_schedule_by_day(day)  # Получаем расписание из таблицы
    bot.send_message(call.message.chat.id, schedule)


# Обработчик кнопки "⬅ Назад"
@bot.callback_query_handler(func=lambda call: call.data == "back")
def go_back(call):
    try:
        bot.edit_message_text("Выберите неделю:", call.message.chat.id, call.message.message_id, reply_markup=main_menu())
    except telebot.apihelper.ApiException:
        bot.send_message(call.message.chat.id, "Выберите неделю:", reply_markup=main_menu())



@bot.message_handler(commands=['cast'])
def send_broadcast(message):
    # Проверяем, что сообщение пришло от администратора (замените на свой ID)
    if message.from_user.id == 1077090809:  # Замените на свой ID
        bot.send_message(message.chat.id, "Введите сообщение для рассылки всем пользователям:")
        bot.register_next_step_handler(message, broadcast_message)
    else:
        bot.send_message(message.chat.id, "У вас нет прав для использования этой команды.")
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
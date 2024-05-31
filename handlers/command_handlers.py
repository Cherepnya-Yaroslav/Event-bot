from config.settings import DB_PATH
from config.settings import ADMIN_USER_ID
import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    welcome_message = (
        f"Привет, {user.first_name}! 👋\n\n"
        "Добро пожаловать в нашего бота для управления событиями! "
        "Вот что вы можете сделать:\n\n"
        "1. Просматривать и добавлять события в избранное.\n"
        "2. Искать события по дате.\n"
        "3. Предлагать свои мероприятия на рассмотрение.\n\n"
        "Используйте команду /menu для вызова главного меню."
    )
    await update.message.reply_text(welcome_message)

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Избранное", callback_data='favorites')],
        [InlineKeyboardButton("Поиск событий", callback_data='search')],
        [InlineKeyboardButton("Предложить событие", callback_data='my_events')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите опцию:', reply_markup=reply_markup)


async def moderate_suggestions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:



    user_id = update.message.from_user.id
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, user_id, date, title, description, image_path, status FROM suggestions WHERE status = "в обработке"')
    suggestions = cursor.fetchall()
    conn.close()

    if suggestions:
        for suggestion_id, user_id, date, title, description, image_path, status in suggestions:
            keyboard = [
                [InlineKeyboardButton("Принять", callback_data=f'approve_{suggestion_id}')],
                [InlineKeyboardButton("Отклонить", callback_data=f'reject_{suggestion_id}')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            if image_path:
                await update.message.reply_photo(photo=image_path,
                                                 caption=f"ID: {suggestion_id}\nДата: {date}\nНазвание: {title}\nОписание: {description}\nСтатус: {status}",
                                                 reply_markup=reply_markup)
            else:
                await update.message.reply_text(
                    f"ID: {suggestion_id}\nДата: {date}\nНазвание: {title}\nОписание: {description}\nСтатус: {status}",
                    reply_markup=reply_markup)
    else:
        await update.message.reply_text("Нет заявок на модерацию.")

async def show_suggestions_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    import sqlite3
    from config.settings import DB_PATH

    user_id = update.message.from_user.id
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT date, title, description, status FROM suggestions WHERE user_id = ?', (user_id,))
    suggestions = cursor.fetchall()
    conn.close()
    if suggestions:
        message = "Ваши заявки:\n\n" + "\n\n".join(
            [f"Дата: {date}\nНазвание: {title}\nОписание: {description}\nСтатус: {status}" for
             date, title, description, status in suggestions])
    else:
        message = "У вас нет заявок."
    await update.message.reply_text(message)


async def clear_all_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.id != ADMIN_USER_ID:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    if 'clear_all_date' not in context.user_data:
        await update.message.reply_text("Пожалуйста, укажите дату в формате ГГГГ-ММ-ДД.")
        context.user_data['state'] = 'clear_all_date'
        return

    date = context.user_data['clear_all_date']
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM suggestions WHERE date <= ?', (date,))
        cursor.execute('DELETE FROM events WHERE date <= ?', (date,))
        cursor.execute('DELETE FROM favorites WHERE event_id IN (SELECT id FROM events WHERE date <= ?)', (date,))
        conn.commit()
        conn.close()
        await update.message.reply_text(f"Все записи из баз данных до {date} включительно были удалены.")
        del context.user_data['clear_all_date']
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")


async def handle_clear_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = context.user_data.get('state')
    date = update.message.text

    if state == 'clear_all_date':
        context.user_data['clear_all_date'] = date
        await clear_all_data(update, context)
    else:
        await update.message.reply_text("Неизвестное состояние. Попробуйте снова.")

    context.user_data['state'] = None

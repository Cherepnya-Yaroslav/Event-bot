from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
import sqlite3
from config.settings import DB_PATH, ADMIN_USER_ID
import datetime
from telegram.constants import ParseMode


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == 'favorites':
        await show_favorites(query, context)
    elif query.data == 'search':
        keyboard = [
            [InlineKeyboardButton((datetime.datetime.now() + datetime.timedelta(days=i)).strftime('%d-%m-%Y'),
                                  callback_data=f'search_date_{(datetime.datetime.now() + datetime.timedelta(days=i)).strftime("%Y-%m-%d")}')
             for i in range(2)],
            [InlineKeyboardButton((datetime.datetime.now() + datetime.timedelta(days=i)).strftime('%d-%m-%Y'),
                                  callback_data=f'search_date_{(datetime.datetime.now() + datetime.timedelta(days=i)).strftime("%Y-%m-%d")}')
             for i in range(2, 4)],
            [InlineKeyboardButton((datetime.datetime.now() + datetime.timedelta(days=i)).strftime('%d-%m-%Y'),
                                  callback_data=f'search_date_{(datetime.datetime.now() + datetime.timedelta(days=i)).strftime("%Y-%m-%d")}')
             for i in range(4, 6)],
            [InlineKeyboardButton((datetime.datetime.now() + datetime.timedelta(days=i)).strftime('%d-%m-%Y'),
                                  callback_data=f'search_date_{(datetime.datetime.now() + datetime.timedelta(days=i)).strftime("%Y-%m-%d")}')
             for i in range(6, 8)],
            [InlineKeyboardButton("Ввести дату", callback_data='search_date_input')],
            [InlineKeyboardButton("События на неделю", callback_data='week_events')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text('Выберите дату поиска:', reply_markup=reply_markup)
    elif query.data.startswith('search_date_'):
        context.user_data['search_date'] = query.data.split('_')[2]
        await search_events_by_date(update, context)
    elif query.data == 'search_date_input':
        await query.message.reply_text('Введите дату в формате ГГГГ-ММ-ДД:')
        context.user_data['state'] = 'search_date'
    elif query.data == 'week_events':
        await search_events_by_week(update, context)
    elif query.data == 'my_events':
        await query.message.reply_text('Введите дату вашего мероприятия в формате ГГГГ-ММ-ДД:')
        context.user_data['state'] = 'my_event_date'
    elif query.data.startswith('approve_') or query.data.startswith('reject_'):
        await handle_moderation(update, context)
    elif query.data.startswith('add_favorite_'):
        await add_favorite(update, context)
    elif query.data.startswith('remove_favorite_'):
        await remove_favorite(update, context)


async def search_events_by_date(update, context):
    date = context.user_data['search_date']
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, description, image_path FROM events WHERE date = ?', (date,))
    events = cursor.fetchall()
    conn.close()
    if events:
        for event_id, title, description, image_path in events:
            keyboard = [[InlineKeyboardButton("Добавить в избранное", callback_data=f'add_favorite_{event_id}')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            if image_path:
                await update.callback_query.message.reply_photo(photo=image_path, caption=f"<b>{title}</b>\n\n{description}",
                                                                reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            else:
                await update.callback_query.message.reply_text(f"<b>{title}</b>\n\n{description}", reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        await update.callback_query.message.reply_text("Нет мероприятий на выбранную дату.")


async def search_events_by_week(update, context):
    start_date = datetime.datetime.now().date()
    end_date = start_date + datetime.timedelta(days=7)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, description, image_path, date FROM events WHERE date BETWEEN ? AND ?',
                   (start_date, end_date))
    events = cursor.fetchall()
    conn.close()

    if events:
        for event_id, title, description, image_path, date in events:
            keyboard = [[InlineKeyboardButton("Добавить в избранное", callback_data=f'add_favorite_{event_id}')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            if image_path:
                await update.callback_query.message.reply_photo(photo=image_path,
                                                                caption=f" <b>{title}</b> \n\n{description}\n\n{date}",
                                                                reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            else:
                await update.callback_query.message.reply_text(f"<b>{title}</b>\n\n{description}\n\n{date}",
                                                               reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        await update.callback_query.message.reply_text("Нет мероприятий на ближайшую неделю.")


async def add_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    event_id = int(query.data.split('_')[2])
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM favorites WHERE user_id = ? AND event_id = ?', (user_id, event_id))
    already_exists = cursor.fetchone()[0]
    if already_exists:
        await query.answer("Это событие уже добавлено в избранное.")
    else:
        cursor.execute('INSERT INTO favorites (user_id, event_id) VALUES (?, ?)', (user_id, event_id))
        conn.commit()
        await query.answer("Добавлено в избранное")
        await query.message.reply_text("Вы добавили событие в избранное.")

    message = query.message
    if message.photo:
        await message.edit_caption(caption=message.caption, reply_markup=None)
    else:
        await message.edit_text(text=message.text, reply_markup=None)
    conn.close()


async def remove_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    event_id = int(query.data.split('_')[2])
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM favorites WHERE user_id = ? AND event_id = ?', (user_id, event_id))
    conn.commit()
    conn.close()
    await query.answer("Удалено из избранного")

    message = query.message
    if message.photo:
        await message.edit_caption(caption=message.caption, reply_markup=None)
    else:
        await message.edit_text(text=message.text, reply_markup=None)
    await query.message.reply_text("Вы удалили событие из избранного.")




async def show_favorites(query, context):
    user_id = query.from_user.id
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''SELECT e.id, e.date, e.title, e.description, e.image_path FROM events e
                      JOIN favorites f ON e.id = f.event_id
                      WHERE f.user_id = ?''', (user_id,))
    events = cursor.fetchall()
    conn.close()
    if events:
        for event_id, date, title, description, image_path in events:
            keyboard = [[InlineKeyboardButton("Удалить из избранного", callback_data=f'remove_favorite_{event_id}')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            if image_path:
                await query.message.reply_photo(photo=image_path,
                                                caption=f" {title}\n\n {description}\n\n {date}",
                                                reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            else:
                await query.message.reply_text(f" {title}\n\n {description}\n\n{date} ",
                                               reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        await query.message.reply_text("У вас нет избранных событий.")

async def handle_moderation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    admin_user_id = query.from_user.id

    if admin_user_id != ADMIN_USER_ID:
        await query.answer("У вас нет прав для выполнения этого действия.")
        return

    action, suggestion_id = query.data.split('_')
    suggestion_id = int(suggestion_id)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if action == 'approve':
        cursor.execute('SELECT date, title, description, image_path FROM suggestions WHERE id = ?', (suggestion_id,))
        suggestion = cursor.fetchone()
        if suggestion:
            date, title, description, image_path = suggestion
            cursor.execute('INSERT INTO events (date, title, description, image_path) VALUES (?, ?, ?, ?)',
                           (date, title, description, image_path))
            cursor.execute('UPDATE suggestions SET status = "принято" WHERE id = ?', (suggestion_id,))
            await query.answer("Заявка принята и добавлена в события.")
        else:
            await query.answer("Заявка не найдена.")
    elif action == 'reject':
        cursor.execute('UPDATE suggestions SET status = "отклонено" WHERE id = ?', (suggestion_id,))
        await query.answer("Заявка отклонена.")
    else:
        await query.answer("Неизвестное действие.")
        return

    cursor.execute('SELECT user_id, date, title, description, image_path FROM suggestions WHERE id = ?',
                   (suggestion_id,))
    user_row = cursor.fetchone()
    if user_row:
        user_id, date, title, description, image_path = user_row
        status_text = "принято" if action == 'approve' else "отклонено"
        await context.bot.send_message(chat_id=user_id, text=f"Ваша заявка с ID {suggestion_id} была {status_text}")

        if image_path:
            await query.message.edit_caption(
                caption=f"ID: {suggestion_id}\nДата: {date}\nНазвание: {title}\nОписание: {description}\nСтатус: {status_text}",
                reply_markup=None)
        else:
            await query.message.edit_text(
                text=f"ID: {suggestion_id}\nДата: {date}\nНазвание: {title}\nОписание: {description}\nСтатус: {status_text}",
                reply_markup=None)
    else:
        print(f"User not found for suggestion_id: {suggestion_id}")

    conn.commit()
    conn.close()

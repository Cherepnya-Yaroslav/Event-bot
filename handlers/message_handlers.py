from telegram import Update
from telegram.ext import ContextTypes
from utils.validation import validate_date
from handlers.callback_handlers import search_events_by_date
import sqlite3
from config.settings import DB_PATH

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    state = context.user_data.get('state')

    if state == 'search_date':
        date = update.message.text
        if not validate_date(date):
            await update.message.reply_text(
                'Дата не может быть в прошлом. Введите корректную дату в формате ГГГГ-ММ-ДД:')
            return
        context.user_data['search_date'] = date
        await search_events_by_date(update, context)
        context.user_data['state'] = None

    elif state == 'my_event_date':
        date = update.message.text
        if not validate_date(date):
            await update.message.reply_text(
                'Дата не может быть в прошлом. Введите корректную дату в формате ГГГГ-ММ-ДД:')
            return
        context.user_data['my_event_date'] = date
        await update.message.reply_text('Введите название вашего мероприятия:')
        context.user_data['state'] = 'my_event_title'

    elif state == 'my_event_title':
        title = update.message.text
        context.user_data['my_event_title'] = title
        await update.message.reply_text('Введите описание вашего мероприятия:')
        context.user_data['state'] = 'my_event_description'

    elif state == 'my_event_description':
        description = update.message.text
        context.user_data['my_event_description'] = description
        await update.message.reply_text('Отправьте изображение для вашего мероприятия или введите "нет":')
        context.user_data['state'] = 'my_event_image'

    elif state == 'my_event_image':
        if update.message.text.lower() == 'нет':
            context.user_data['my_event_image'] = None
            date = context.user_data['my_event_date']
            title = context.user_data['my_event_title']
            description = context.user_data['my_event_description']
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO suggestions (user_id, date, title, description, image_path) VALUES (?, ?, ?, ?, ?)',
                           (user_id, date, title, description, None))
            conn.commit()
            conn.close()
            await update.message.reply_text('Ваше мероприятие предложено администратору на рассмотрение.')
            context.user_data['state'] = None
        else:
            await update.message.reply_text('Пожалуйста, отправьте изображение или введите "нет".')


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    import sqlite3
    from config.settings import DB_PATH

    user_id = update.message.from_user.id
    state = context.user_data.get('state')

    if state == 'my_event_image':
        image_path = update.message.photo[-1].file_id
        context.user_data['my_event_image'] = image_path
        date = context.user_data['my_event_date']
        title = context.user_data['my_event_title']
        description = context.user_data['my_event_description']
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO suggestions (user_id, date, title, description, image_path) VALUES (?, ?, ?, ?, ?)',
                       (user_id, date, title, description, image_path))
        conn.commit()
        conn.close()
        await update.message.reply_text('Ваше мероприятие предложено администратору на рассмотрение.')
        context.user_data['state'] = None

from telegram import Update
from telegram.ext import ContextTypes

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    if 'started' not in context.user_data:
        context.user_data['started'] = True
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

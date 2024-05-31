from config.settings import TOKEN
from database.db_manager import init_db
from handlers.command_handlers import start, menu, moderate_suggestions, show_suggestions_status
from handlers.callback_handlers import button
from handlers.message_handlers import handle_message, handle_photo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from handlers.onboarding import welcome

def main() -> None:
    init_db()

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("moderate", moderate_suggestions))
    application.add_handler(CommandHandler("status", show_suggestions_status))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.ALL, welcome))

    application.run_polling()

if __name__ == '__main__':
    main()

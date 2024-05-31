import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
DB_PATH = os.getenv('DB_PATH')
ADMIN_USER_ID = os.getenv('ADMIN_USER_ID')

# Проверка и вывод ошибок
if TOKEN is None:
    raise ValueError("Переменная окружения TOKEN не задана")
if DB_PATH is None:
    raise ValueError("Переменная окружения DB_PATH не задана")
if ADMIN_USER_ID is None:
    raise ValueError("Переменная окружения ADMIN_USER_ID не задана")
else:
    ADMIN_USER_ID = int(ADMIN_USER_ID)

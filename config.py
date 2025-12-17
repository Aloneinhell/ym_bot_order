import os

import dotenv
from aiogram import Bot

import pytz
from datetime import datetime

# Московский часовой пояс
moscow_tz = pytz.timezone('Europe/Moscow')

dotenv.load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))

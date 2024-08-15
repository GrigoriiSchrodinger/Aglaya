from os import getenv

from aiogram import Dispatcher
from dotenv import load_dotenv

load_dotenv()

TOKEN = getenv("BOT_TOKEN")
DP = Dispatcher()

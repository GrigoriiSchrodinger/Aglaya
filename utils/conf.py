import os

from aiogram import Dispatcher
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
DP = Dispatcher()
PATH_SAVED_VIDEO = str(Path.cwd()) + "/saved_video/"

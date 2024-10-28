from aiogram.filters.state import StatesGroup, State


class DownloadForm(StatesGroup):
    download_link = State()
    download_state = State()
    quality = State()
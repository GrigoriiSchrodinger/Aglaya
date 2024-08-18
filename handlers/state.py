from aiogram.filters.state import StatesGroup, State


class DownloadForm(StatesGroup):
    download_state = State()

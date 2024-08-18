import asyncio
import os
import random
import string

from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext

from feature.download import DownloadManager
from handlers.state import DownloadForm
from utils.conf import DP, PATH_SAVED_VIDEO


@DP.message(Command("download"))
async def command_download(message: Message, state: FSMContext) -> None:
    await state.set_state(DownloadForm.download_state)
    await message.answer(
        text=f"Отправь мне ссылку на видео",
    )


@DP.message(DownloadForm.download_state)
async def process_download(message: Message):
    youtube_url = message.text
    name = ''.join(random.sample(string.ascii_lowercase, 4)) + ".mp4"
    download_manager = DownloadManager(id_name=name, url=youtube_url)
    video_info = download_manager.get_info_video()
    start_message = await message.answer(text="Начинаем загрузку")

    asyncio.create_task(update_download_status(start_message, download_manager))
    await download_manager.download_video_async()

    video_file = FSInputFile(path=os.path.join(PATH_SAVED_VIDEO, name))
    if is_file_size_acceptable(PATH_SAVED_VIDEO + name):
        sending_message = await message.answer(text="Уже отправляем, еще чуть чуть)")
        await message.answer_video(video=video_file, caption=f"{video_info['title']}\nДлительность - {seconds_to_hms(video_info['duration'])}\nПросмотров - {video_info['view_count']}")
        await sending_message.delete()
    else:
        await message.answer(text="Файл слишком большой для отправки, пока что видео макс до 15 минут")
    download_manager.delete_video()


async def update_download_status(start_message: Message, download_manager: DownloadManager):
    previous_status = ""
    video_info = download_manager.get_info_video()
    while download_manager.download_status != "Download finished":
        current_status = download_manager.get_download_status()["status"]
        if current_status != "Not started" and "finished":
            message_text = f"{video_info['title']}\nДлительность - {seconds_to_hms(video_info['duration'])}\nПросмотров - {video_info['view_count']}\n\nЗагружено -{current_status['percent']}"
            if current_status != previous_status:
                await start_message.edit_text(text=message_text)
                previous_status = current_status
            await asyncio.sleep(1)
    await start_message.delete()


def seconds_to_hms(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def is_file_size_acceptable(file_path, max_size_mb=50):
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    return file_size_mb <= max_size_mb

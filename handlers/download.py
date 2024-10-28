import asyncio
import os
import random
import string

from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext

from feature.download import DownloadManager
from handlers.state import DownloadForm
from utils.conf import DP, PATH_SAVED_VIDEO


@DP.message(Command("download"))
async def command_download(message: Message, state: FSMContext):
    quality_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Плохое", callback_data="quality_low")],
            [InlineKeyboardButton(text="Среднее", callback_data="quality_medium")],
            [InlineKeyboardButton(text="Лучшее", callback_data="quality_high")]
        ]
    )

    await state.set_state(DownloadForm.quality)
    reply_message = await message.answer("Выберите качество видео:", reply_markup=quality_keyboard)

    await state.update_data(reply_message_id=reply_message.message_id)


@DP.callback_query(lambda c: c.data in ["quality_low", "quality_medium", "quality_high"])
async def process_quality_choice(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(quality=callback_query.data)

    data = await state.get_data()
    reply_message_id = data.get("reply_message_id")

    await callback_query.message.bot.delete_message(callback_query.message.chat.id, reply_message_id)
    await callback_query.message.answer("Отправь ссылку на видео для загрузки.")

    await state.set_state(DownloadForm.download_link)
    await callback_query.answer()


@DP.message(DownloadForm.download_link)
async def process_download(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        quality = data.get("quality")

        youtube_url = message.text
        name = ''.join(random.sample(string.ascii_lowercase, 4)) + ".mp4"

        download_manager = DownloadManager(id_name=name, url=youtube_url, resolution=quality)
        video_info = download_manager.get_info_video()
        start_message = await message.answer(text="Начинаем загрузку...")

        asyncio.create_task(update_download_status(start_message, download_manager))
        await download_manager.download_video_async()

        video_file = FSInputFile(path=os.path.join(PATH_SAVED_VIDEO, name))
        try:
            if is_file_size_acceptable(PATH_SAVED_VIDEO + name):
                sending_message = await message.answer(text="Уже отправляем, еще чуть чуть...")
                await message.answer_document(
                    document=video_file,
                    caption=f"{video_info['title']}\nДлительность - {seconds_to_hms(video_info['duration'])}\nПросмотров - {video_info['view_count']}"
                )
                await sending_message.delete()
            else:
                await message.answer(text="Файл слишком большой для отправки, пока что видео макс до 15 минут.")
        finally:
            download_manager.delete_video()
            await state.clear()
    except Exception as error:
        print(error)
        await message.answer(text="С ссылкой похоже что-то не то, давай попробуем еще раз")
        await state.clear()

async def update_download_status(start_message: Message, download_manager: DownloadManager):
    previous_status = ""
    video_info = download_manager.get_info_video()
    while download_manager.download_status != "Download finished":
        current_status = download_manager.get_download_status()["status"]
        if current_status != "Not started" and current_status != "finished":
            message_text = f"{video_info['title']}\nДлительность - {seconds_to_hms(video_info['duration'])}\nПросмотров - {video_info['view_count']}\n\nЗагружено - {current_status['percent']}"
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
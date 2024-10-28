import os
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from feature.translator import Translator
from utils.conf import DP, PATH_SAVED_VIDEO


async def translator_audio_video(message: Message, file_message):
    file_id = file_message.file_id
    file = await message.bot.get_file(file_id)

    destination = os.path.join(PATH_SAVED_VIDEO, f"{file_id}.mp3")
    await message.bot.download_file(file.file_path, destination)

    # Отправляем начальное сообщение
    sent_message = await message.reply("Еще секундочку, пожалуйста...")

    translator = Translator(destination)
    transcribed_text = ""

    # Постепенно обрабатываем каждый сегмент текста и обновляем сообщение
    async for text_segment in translator.transcribe():
        transcribed_text += text_segment + " "
        await sent_message.edit_text(transcribed_text.strip())  # Обновляем сообщение

@DP.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    if message.video_note:
        media = message.video_note
    elif message.voice:
        media = message.voice
    else:
        await message.answer(f"Приветик, {hbold(message.from_user.first_name)}!")
        return
    await translator_audio_video(message, media)
import asyncio
import logging
import sys

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from handlers.start import command_start_handler
from utils.conf import TOKEN, DP

commands_handlers = [
    command_start_handler
]


async def main() -> None:
    for handler in commands_handlers:
        DP.message.register(handler)

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await DP.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

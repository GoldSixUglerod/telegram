import logging

from aiogram import executor

from bot.loader import dp


async def on_startup(dispatcher):
    import bot.handlers


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, on_startup=on_startup)

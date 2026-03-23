import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import BOT_TOKEN
import db
from handlers import register_handlers

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def main():
    db.init_db()
    register_handlers(dp)

    # Установка команд бота
    await bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("profile", "Мой профиль"),
        types.BotCommand("mycars", "Мои машины"),
    ])

    logging.info("Бот запущен")
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
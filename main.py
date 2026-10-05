import asyncio
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config.settings import load_settings
from handlers import common, stats, workouts
from scheduler.reminders import dispatch_due_reminders
from services.storage import Storage


async def main() -> None:
    settings = load_settings()
    logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    storage = Storage(Path("data/champion_mode.json"))
    await storage.load()

    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp["storage"] = storage
    dp["settings"] = settings
    dp.include_routers(common.router, workouts.router, stats.router)

    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(dispatch_due_reminders, "cron", second=0, args=[bot, storage], id="reminders", replace_existing=True)
    scheduler.start()
    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())


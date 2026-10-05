from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from services.training_catalog import planned_days_in_month

router = Router()


async def stats_text(storage, telegram_id: int) -> str | None:
    user = await storage.get_user(telegram_id)
    if not user:
        return None
    today = datetime.now(ZoneInfo(user["timezone"])).date()
    stats = await storage.monthly_stats(telegram_id, today.year, today.month)
    planned = planned_days_in_month(today)
    percent = round(stats["completed"] / planned * 100) if planned else 0
    return f"""<b>CHAMPION MODE — OCTOBER</b>

Выполнено тренировок: {stats['completed']} / {planned}
Стойка: {stats['handstand']}
Шея: {stats['neck']}
Экспандер: {stats['gripper']}
Речь: {stats['speech']}

🔥 Текущая серия: {user['current_streak']}
🏆 Максимальная серия: {user['max_streak']}
📈 Процент выполнения: {percent}%"""


@router.message(Command("stats"))
async def stats(message: Message, storage):
    text = await stats_text(storage, message.from_user.id)
    await message.answer(text or "Сначала включи режим через /start.")


@router.callback_query(F.data == "stats:show")
async def callback_stats(callback: CallbackQuery, storage):
    text = await stats_text(storage, callback.from_user.id)
    await callback.message.answer(text or "Сначала включи режим через /start.")
    await callback.answer()

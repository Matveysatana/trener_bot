import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Bot

from keyboards.inline import main_keyboard, reminder_keyboard
from services.texts import MORNING
from services.training_catalog import MODULE_LABELS, is_training_day

logger = logging.getLogger(__name__)


async def dispatch_due_reminders(bot: Bot, storage) -> None:
    for telegram_id, user in await storage.users():
        try:
            now = datetime.now(ZoneInfo(user["timezone"]))
            if not is_training_day(now.date()):
                await storage.refresh_missed_streak(telegram_id, now.date())
                continue
            _, workout = await storage.today(telegram_id, now.date())
            if workout["completed"]:
                continue
            if now.hour == 7 and not workout["morning_sent"]:
                await bot.send_message(telegram_id, MORNING, reply_markup=main_keyboard())
                await storage.mark_notification(telegram_id, now.date(), "morning_sent")
            elif now.hour in (17, 19):
                field = "reminder_17_sent" if now.hour == 17 else "reminder_19_sent"
                if not workout[field]:
                    remaining = "\n".join(f"• {MODULE_LABELS[module]}" for module, item in workout["modules"].items() if not item["completed"])
                    text = (f"Чемпион, тренировка ещё не закрыта.\n\nУ тебя впереди вечер.\n\nОсталось:\n{remaining}\n\n25–30 минут — и сегодняшний день засчитан."
                            if now.hour == 17 else f"Последний вызов на сегодня.\n\nНе нужно ждать мотивации.\n\nПросто начни с первого упражнения.\n\nОсталось:\n{remaining}")
                    await bot.send_message(telegram_id, text, reply_markup=reminder_keyboard(now.hour == 19))
                    await storage.mark_notification(telegram_id, now.date(), field)
        except Exception:
            logger.exception("Не удалось отправить напоминание пользователю %s", telegram_id)

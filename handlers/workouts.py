from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from keyboards.inline import main_keyboard, modules_keyboard
from services.training_catalog import MODULE_LABELS, is_training_day, protocol_for
from services.texts import COMPLETED

router = Router()


async def today_view(storage, telegram_id: int):
    user = await storage.get_user(telegram_id)
    if not user:
        return None, None, None
    day = datetime.now(ZoneInfo(user["timezone"])).date()
    if not is_training_day(day):
        return user, day, None
    user, workout = await storage.today(telegram_id, day)
    return user, day, workout


@router.message(Command("today"))
async def today(message: Message, storage):
    user, day, workout = await today_view(storage, message.from_user.id)
    if not user:
        await message.answer("Сначала включи режим через /start.")
    elif not workout:
        await message.answer("Сегодня день восстановления. Обязательной тренировки нет — восстановись и возвращайся сильнее в понедельник, среду или пятницу.")
    elif workout["completed"]:
        await message.answer("Сегодняшняя тренировка уже закрыта. 🔥")
    else:
        await message.answer("Сегодня тренировочный день. Готов к работе?", reply_markup=main_keyboard())


@router.callback_query(F.data == "workout:show")
async def show_workout(callback: CallbackQuery, storage):
    user, day, workout = await today_view(storage, callback.from_user.id)
    if not user:
        await callback.answer("Сначала запусти /start", show_alert=True)
        return
    if not workout:
        await callback.answer("Сегодня обязательной тренировки нет", show_alert=True)
        return
    await callback.message.answer(protocol_for(day), reply_markup=main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "workout:mark")
async def mark_workout(callback: CallbackQuery, storage):
    user, day, workout = await today_view(storage, callback.from_user.id)
    if not workout:
        await callback.answer("Сегодня нет обязательной тренировки", show_alert=True)
        return
    rows = await storage.module_rows(callback.from_user.id, day)
    await callback.message.answer("Отмечай модули по мере выполнения:", reply_markup=modules_keyboard(rows))
    await callback.answer()


@router.callback_query(F.data.startswith("module:"))
async def mark_module(callback: CallbackQuery, storage):
    module = callback.data.split(":", 1)[1]
    user, day, workout = await today_view(storage, callback.from_user.id)
    if not workout or module not in MODULE_LABELS:
        await callback.answer("Эта тренировка сейчас недоступна", show_alert=True)
        return
    finished, streak, achievement = await storage.complete_module(callback.from_user.id, day, module)
    rows = await storage.module_rows(callback.from_user.id, day)
    await callback.message.edit_reply_markup(reply_markup=modules_keyboard(rows))
    await callback.answer("Отмечено! 🔥")
    if finished:
        await callback.message.answer(COMPLETED.format(streak=streak))
        if achievement:
            await callback.message.answer(f"🏆 Новый уровень: <b>{achievement}</b>\nПродолжай держать режим!")


@router.message(Command("gripper"))
async def gripper_result(message: Message, storage):
    value = message.text.partition(" ")[2].strip()
    if not value:
        await message.answer("Напиши результат так: <code>/gripper 3×15, 40 кг</code>")
        return
    user, day, workout = await today_view(storage, message.from_user.id)
    if not workout:
        await message.answer("Результат экспандера можно сохранить в тренировочный день.")
        return
    finished, streak, achievement = await storage.complete_module(message.from_user.id, day, "gripper", value)
    await message.answer("Результат экспандера сохранён. ✊")
    if finished:
        await message.answer(COMPLETED.format(streak=streak))
        if achievement:
            await message.answer(f"🏆 Новый уровень: <b>{achievement}</b>\nПродолжай держать режим!")

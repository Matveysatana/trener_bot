from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from keyboards.inline import welcome_keyboard
from services.texts import WELCOME

router = Router()


@router.message(CommandStart())
async def start(message: Message, storage):
    if await storage.get_user(message.from_user.id):
        await message.answer("Режим уже включён, чемпион. Используй /today, чтобы открыть план на сегодня.")
        return
    await message.answer(WELCOME, reply_markup=welcome_keyboard())


@router.callback_query(F.data == "mode:join")
async def join_mode(callback: CallbackQuery, storage, settings):
    await storage.join(callback.from_user.id, callback.from_user.full_name, settings.default_timezone)
    await callback.message.edit_text("Режим включён. 🔥\n\nБлижайшая тренировка — в понедельник, среду или пятницу. Открыть план можно командой /today.")
    await callback.answer("Добро пожаловать в режим!")


@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer("/today — тренировка на сегодня\n/stats — статистика за текущий месяц\n/gripper 3×15, 40 кг — сохранить результат экспандера\n/help — эта подсказка")

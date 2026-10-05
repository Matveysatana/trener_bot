from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from services.training_catalog import MODULE_LABELS


def welcome_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔥 Войти в режим", callback_data="mode:join")]])


def main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Начать тренировку", callback_data="workout:show")],
        [InlineKeyboardButton(text="✅ Отметить выполнение", callback_data="workout:mark")],
        [InlineKeyboardButton(text="📊 Прогресс", callback_data="stats:show")],
    ])


def modules_keyboard(rows) -> InlineKeyboardMarkup:
    buttons = []
    for row in rows:
        label = MODULE_LABELS[row["module"]]
        text = f"✅ {label[2:]}" if row["completed"] else f"⬜ {label[2:]}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"module:{row['module']}")])
    buttons.append([InlineKeyboardButton(text="↩️ К тренировке", callback_data="workout:show")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def reminder_keyboard(last: bool = False) -> InlineKeyboardMarkup:
    if last:
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔥 Начинаю сейчас", callback_data="workout:show")]])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Продолжить", callback_data="workout:show")],
        [InlineKeyboardButton(text="✅ Отметить выполнение", callback_data="workout:mark")],
    ])


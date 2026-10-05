from calendar import monthrange
from datetime import date

MODULES = ("handstand", "neck", "gripper", "speech")
MODULE_LABELS = {
    "handstand": "🤸 Стойка",
    "neck": "🦾 Шея",
    "gripper": "✊ Экспандер",
    "speech": "🎙 Речь",
}

WEEK_LABELS = {
    1: "Неделя 1 — адаптация",
    2: "Неделя 2 — стабильность",
    3: "Неделя 3 — небольшое увеличение объёма",
    4: "Неделя 4 — закрепление и контроль",
    5: "Финальные дни — тестирование",
}


def is_training_day(day: date) -> bool:
    return day.weekday() in (0, 2, 4)


def training_week(day: date) -> int:
    if day.day > 28:
        return 5
    return (day.day - 1) // 7 + 1


def protocol_for(day: date) -> str:
    week = training_week(day)
    extra = "Добавь 1 подход или 2–3 контролируемые попытки." if week == 3 else "Работай спокойно, без рывков."
    if week == 5:
        extra = "Отметь лучший качественный результат месяца, без работы на износ."
    return f"""{WEEK_LABELS[week]}

🤸 <b>Стойка на руках</b> · 8–12 минут
Разминка кистей и плеч → стойка у стены → контролируемый отрыв ног. При уверенном уровне — свободные попытки.

🦾 <b>Шея</b> · 5–10 минут
Лёгкая разминка → изометрия вперёд, назад, влево и вправо. Только мягкое контролируемое усилие — без мостов и большой нагрузки.

✊ <b>Экспандер</b>
3 подхода по 10–15 повторений: правая, затем левая рука. При желании сохрани повторения или сопротивление.

🎙 <b>Речь</b> · 5–10 минут
Дыхание → «М» на резонанс → вибрация губ → ПА–БА–ТА–ДА–КА–ГА → скороговорка → чтение вслух → минута импровизации.

<i>{extra}</i>"""


def planned_days_in_month(day: date) -> int:
    return sum(is_training_day(date(day.year, day.month, n)) for n in range(1, monthrange(day.year, day.month)[1] + 1))


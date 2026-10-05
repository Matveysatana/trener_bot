"""Небольшое локальное хранилище без внешней базы данных."""
from __future__ import annotations

import asyncio
import copy
import json
from datetime import date, datetime, timedelta
from pathlib import Path

from services.training_catalog import MODULES, is_training_day
from services.texts import ACHIEVEMENTS


class Storage:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data: dict = {"users": {}}
        self.lock = asyncio.Lock()

    async def load(self) -> None:
        if self.path.exists():
            self.data = json.loads(await asyncio.to_thread(self.path.read_text, encoding="utf-8"))

    async def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        await asyncio.to_thread(temporary.write_text, json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
        await asyncio.to_thread(temporary.replace, self.path)

    async def get_user(self, telegram_id: int) -> dict | None:
        async with self.lock:
            user = self.data["users"].get(str(telegram_id))
            return copy.deepcopy(user) if user else None

    async def users(self) -> list[tuple[int, dict]]:
        async with self.lock:
            return [(int(user_id), copy.deepcopy(user)) for user_id, user in self.data["users"].items()]

    async def join(self, telegram_id: int, name: str, timezone: str) -> dict:
        async with self.lock:
            key = str(telegram_id)
            user = self.data["users"].setdefault(key, {"name": name, "timezone": timezone, "registered_at": datetime.now().isoformat(), "current_streak": 0, "max_streak": 0, "achievements": [], "workouts": {}})
            await self._save()
            return copy.deepcopy(user)

    def _workout(self, user: dict, day: date, create: bool = True) -> dict | None:
        key = day.isoformat()
        if key not in user["workouts"] and create and is_training_day(day):
            user["workouts"][key] = {"planned": True, "completed": False, "completed_at": None, "morning_sent": False, "reminder_17_sent": False, "reminder_19_sent": False, "modules": {module: {"completed": False, "completed_at": None, "result": None} for module in MODULES}}
        return user["workouts"].get(key)

    async def today(self, telegram_id: int, day: date) -> tuple[dict | None, dict | None]:
        async with self.lock:
            user = self.data["users"].get(str(telegram_id))
            if not user:
                return None, None
            workout = self._workout(user, day)
            await self._save()
            return copy.deepcopy(user), copy.deepcopy(workout) if workout else None

    async def module_rows(self, telegram_id: int, day: date) -> list[dict]:
        async with self.lock:
            workout = self._workout(self.data["users"][str(telegram_id)], day)
            return [{"module": module, **workout["modules"][module]} for module in MODULES]

    async def complete_module(self, telegram_id: int, day: date, module: str, value: str | None = None) -> tuple[bool, int, str | None]:
        async with self.lock:
            user = self.data["users"][str(telegram_id)]
            workout = self._workout(user, day)
            entry = workout["modules"][module]
            entry["completed"] = True
            entry["completed_at"] = entry["completed_at"] or datetime.now().isoformat()
            if value:
                entry["result"] = value
            finished, achievement = False, None
            if not workout["completed"] and all(item["completed"] for item in workout["modules"].values()):
                workout["completed"] = True
                workout["completed_at"] = datetime.now().isoformat()
                finished = True
                streak = self._recalculate_streak(user, day)
                total = sum(1 for item in user["workouts"].values() if item["completed"])
                if total in ACHIEVEMENTS and ACHIEVEMENTS[total] not in user["achievements"]:
                    achievement = ACHIEVEMENTS[total]
                    user["achievements"].append(achievement)
            else:
                streak = user["current_streak"]
            await self._save()
            return finished, streak, achievement

    def _recalculate_streak(self, user: dict, day: date) -> int:
        streak, current = 0, day
        while is_training_day(current):
            workout = user["workouts"].get(current.isoformat())
            if not workout or not workout["completed"]:
                break
            streak += 1
            current -= timedelta(days=1)
            while not is_training_day(current):
                current -= timedelta(days=1)
        user["current_streak"] = streak
        user["max_streak"] = max(user["max_streak"], streak)
        return streak

    async def refresh_missed_streak(self, telegram_id: int, today: date) -> None:
        async with self.lock:
            user = self.data["users"].get(str(telegram_id))
            if not user:
                return
            previous = today - timedelta(days=1)
            while not is_training_day(previous):
                previous -= timedelta(days=1)
            workout = user["workouts"].get(previous.isoformat())
            if not workout or not workout["completed"]:
                user["current_streak"] = 0
                await self._save()

    async def mark_notification(self, telegram_id: int, day: date, field: str) -> None:
        async with self.lock:
            workout = self._workout(self.data["users"][str(telegram_id)], day)
            workout[field] = True
            await self._save()

    async def monthly_stats(self, telegram_id: int, year: int, month: int) -> dict[str, int]:
        async with self.lock:
            user = self.data["users"][str(telegram_id)]
            workouts = [item for key, item in user["workouts"].items() if date.fromisoformat(key).year == year and date.fromisoformat(key).month == month]
            return {"completed": sum(item["completed"] for item in workouts), **{module: sum(item["modules"][module]["completed"] for item in workouts) for module in MODULES}}

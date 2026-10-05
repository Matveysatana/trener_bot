# CHAMPION MODE

Лёгкий асинхронный Telegram-бот-тренер. PostgreSQL и Docker не нужны: прогресс хранится локально в `data/champion_mode.json`.

## Запуск

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

Откройте `.env` и заполните `BOT_TOKEN`, затем запустите:

```powershell
py main.py
```

Файл с прогрессом создаётся автоматически после первого действия пользователя. Команды: `/today`, `/stats`, `/gripper 3×15, 40 кг`, `/help`.

## Удаление старой Docker-базы

Если ранее запускалась предыдущая версия, удалите её один раз:

```powershell
docker rm -f champion-mode-db
docker volume rm trener_champion_mode_postgres
```

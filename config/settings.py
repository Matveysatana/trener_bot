from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    bot_token: str
    default_timezone: str
    log_level: str


def load_settings() -> Settings:
    load_dotenv()
    token = os.getenv("BOT_TOKEN", "")
    if not token:
        raise RuntimeError("Заполните BOT_TOKEN в .env")
    return Settings(
        bot_token=token,
        default_timezone=os.getenv("DEFAULT_TIMEZONE", "Europe/Moscow"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )


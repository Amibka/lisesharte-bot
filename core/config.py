import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    def __init__(self) -> None:
        self.DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
        self.BOT_TOKEN: str = os.getenv("BOT_TOKEN")

        self.WINDOW_MEMORY_LIMIT: int = int(os.getenv("WINDOW_MEMORY_LIMIT", 20))
        self.DB_PROVIDER: str = os.getenv("DB_PROVIDER", "sqlite").lower()
        self.SQLITE_DB_NAME: str = os.getenv("SQLITE_DB_NAME", "memory_storage.db")

        self.DATABASE_USER = os.getenv("DATABASE_USER", "user")
        self.DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "pass")
        self.DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
        self.DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
        self.DATABASE_NAME = os.getenv("DATABASE_NAME", "dbname")

        self.IP: str = os.getenv("IP")
        self.PORT: int = int(os.getenv("PORT"))
        self.REDIS_URL: str = os.getenv("REDIS_URL")

        self.LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "lm-studio")
        self.MODEL: str = os.getenv("MODEL")
        self.CONTEXT_LENGTH: int = int(os.getenv("CONTEXT_LENGTH"))
        self.FLASH_ATTENTION: bool = os.getenv("FLASH_ATTENTION", "False").lower() in (
            "true",
            "1",
            "yes",
        )
        self.OFFLOAD_KV_CACHE_TO_GPU: bool = os.getenv(
            "OFFLOAD_KV_CACHE_TO_GPU", "False"
        ).lower() in ("true", "1", "yes")
        self.TEMPERATURE: float = float(os.getenv("TEMPERATURE", 0.7))
        self.TOP_P: float = float(os.getenv("TOP_P", 0.9))
        self.FREQUENCY_PENALTY: float = float(os.getenv("FREQUENCY_PENALTY", 0.0))
        self.PRESENCE_PENALTY: float = float(os.getenv("PRESENCE_PENALTY", 0.0))

        self.LM_STUDIO_IP: str = os.getenv("LM_STUDIO_IP", "127.0.0.1")
        self.LM_STUDIO_PORT: str = os.getenv("LM_STUDIO_PORT", "1234")
        self.LLM_API_KEY: str = os.getenv("LLM_API_KEY", "not-needed-for-lm-studio")

        self.LM_STUDIO_BASE: str = f"http://{self.LM_STUDIO_IP}:{self.LM_STUDIO_PORT}"
        self.LM_STUDIO_URL: str = f"{self.LM_STUDIO_BASE}/v1/chat/completions"

        self._validate_config()

    @property
    def DATABASE_URL(self) -> str:
        if self.DB_PROVIDER == "postgres":
            user = os.getenv("POSTGRES_USER")
            password = os.getenv("POSTGRES_PASSWORD")
            host = os.getenv("POSTGRES_HOST", "localhost")
            port = os.getenv("POSTGRES_PORT", "5432")
            db_name = os.getenv("POSTGRES_DB")
            return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"

        return f"sqlite+aiosqlite:///{BASE_DIR / self.SQLITE_DB_NAME}"

    @property
    def FASTAPI_URL(self) -> str:
        ip = self.IP
        port = self.PORT
        return f"http://{ip}:{port}"

    def _validate_config(self) -> None:
        required_fields = {
            "BOT_TOKEN": self.BOT_TOKEN,
            "MODEL": self.MODEL,
            "LM_STUDIO_IP": self.LM_STUDIO_IP,
            "LM_STUDIO_PORT": self.LM_STUDIO_PORT,
            "LLM_API_KEY": self.LLM_API_KEY,
            "IP": self.IP,
            "PORT": self.PORT,
            "REDIS_URL": self.REDIS_URL,
        }

        for field_name, value in required_fields.items():
            if not value:
                raise ValueError(
                    f"Ошибка запуска: в файле .env не найден параметр '{field_name}'!"
                )


config = Config()

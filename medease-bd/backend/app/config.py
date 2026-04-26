import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "MedEase BD"
    VERSION: str = "1.0.0"

    # Database
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "medease")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "medease123")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "medease_db")

    # LLM - optimized for Ryzen 4500U (6 cores, no hyperthreading)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gguf")
    MODEL_PATH: str = os.getenv("MODEL_PATH", "app/models/qwen2.5-1.5b-instruct.Q4_0.gguf")
    LLM_THREADS: int = int(os.getenv("LLM_THREADS", "5"))       # 5 of 6 cores
    LLM_BATCH_SIZE: int = int(os.getenv("LLM_BATCH_SIZE", "32"))
    LLM_CONTEXT_SIZE: int = int(os.getenv("LLM_CONTEXT_SIZE", "512"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "150"))

    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()

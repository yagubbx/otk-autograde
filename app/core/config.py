from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # .env faylından oxunacaq məcburi dəyişənlər
    OPENAI_API_KEY: str
    DATABASE_URL: str
    DEBUG: bool = True
    
    # Layihə üçün sabit dəyişənlər (Sabit olaraq qalır)
    PROJECT_NAME: str = "OTK AutoGrade"
    API_V1_STR: str = "/api/v1"

    # Pydantic-ə deyirik ki, məlumatları .env faylından götür
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# lru_cache proqramın hər dəfə faylı yenidən oxumasının qarşısını alır (sürət üçün)
@lru_cache()
def get_settings():
    return Settings()

# Digər fayllarda istifadə etmək üçün hazır obyekt
settings = get_settings()
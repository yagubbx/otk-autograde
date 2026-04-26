# app/main.py
from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.endpoints import router as api_router
from app.db.session import engine
from app.db.base import Base
import contextlib

# Proqram başlayanda bazadakı cədvəlləri avtomatik yaratmaq üçün
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

# API Marşrutumuzu sistemə əlavə edirik
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
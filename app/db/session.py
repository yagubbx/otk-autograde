from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 1. Mühərrikin (Engine) yaradılması
engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} 
)

# 2. Sessiya Fabriki
AsyncSessionLocal = sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# 3. Asinxron Bağlantı funksiyası
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
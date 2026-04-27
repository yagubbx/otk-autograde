# app/db/models.py
from sqlalchemy import Column, String, Float, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.base import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True, index=True) # sual_id (məs: inf_001)
    
    # Mətn formatında saxlanılan yekun məlumatlar
    sual_metni = Column(Text, nullable=True)
    duzgun_hell = Column(Text, nullable=True)
    meyarlar = Column(Text, nullable=True)
    
    # YENİ: Bu sualın şəkilləri əvvəllər AI tərəfindən oxunubmu? 
    # (Token qənaəti üçün keşləmə bayrağı)
    is_processed = Column(Boolean, default=False)
    
    # Master Prompt üçün hazır vəziyyətə gətirilmiş yekun kontekst
    processed_context = Column(Text, nullable=True) 

    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(String, primary_key=True, index=True) 
    sual_id = Column(String, index=True)
    sagird_id = Column(String, index=True)
    
    # Audit üçün (Kim nə göndərmişdi?)
    sagird_helli_original = Column(Text, nullable=True) # Text idisə text, şəkil idisə "Şəkil göndərilib"
    
    # YENİ: AI-ın şagirdin şəklindən oxuyub çıxardığı mətn
    sagird_helli_transkripsiya = Column(Text, nullable=True) 
    
    verilen_bal = Column(Float, nullable=False)
    serh = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False) 
    raw_ai_response = Column(Text, nullable=False) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
from sqlalchemy import Column, String, Float, Text, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True, index=True) # Sualın unikal kodu (məs: inf_001)
    sual_metni = Column(Text, nullable=False)
    duzgun_hell = Column(Text, nullable=False)
    meyarlar = Column(Text, nullable=False)
    processed_context = Column(Text, nullable=True) # AI üçün "çeynənmiş" hazır prompt

class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(String, primary_key=True, index=True) # Yoxlamanın unikal ID-si
    sual_id = Column(String, index=True)
    sagird_id = Column(String, index=True)
    
    # Audit üçün (Şagird nə yazmışdı?)
    sagird_helli = Column(Text, nullable=False) # Base64 şəkil və ya mətn
    
    # AI-nın verdiyi nəticələr
    verilen_bal = Column(Float, nullable=False)
    serh = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False) # AI özünə nə qədər güvənir?
    raw_ai_response = Column(Text, nullable=False) # AI-dan gələn xam JSON
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
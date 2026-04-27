# app/schemas/evaluation.py
from pydantic import BaseModel, Field
from typing import Optional

# 1. GİRİŞ (İstifadəçidən gələn məlumat)
class EvaluationRequest(BaseModel):
    sual_id: str
    sagird_id: str
    
    # SUAL (Ya mətn, ya şəkil)
    sual_metni: Optional[str] = None
    sual_sekli_base64: Optional[str] = None
    
    # DÜZGÜN HƏLL (Ya mətn, ya şəkil)
    duzgun_hell: Optional[str] = None
    duzgun_hell_sekli_base64: Optional[str] = None
    
    # MEYARLAR (Ya mətn, ya şəkil)
    meyarlar: Optional[str] = None
    meyarlar_sekli_base64: Optional[str] = None
    
    # ŞAGİRDİN HƏLLİ (Ya mətn, ya şəkil)
    sagird_helli_text: Optional[str] = None
    sagird_helli_base64: Optional[str] = None

# 2. ÇIXIŞ (UI-a və ya sistemə qayıdan cavab)
class EvaluationResponse(BaseModel):
    sagird_id: str
    sual_id: str
    
    # YENİ: Sənin istədiyin o "Şəkildə nə gördüm?" izahları
    sualin_analizi: Optional[str] = Field(None, description="AI-ın sual/meyar şəkillərindən çıxardığı mətnlər")
    sagirdin_analizi: Optional[str] = Field(None, description="AI-ın şagirdin şəklindən oxuduğu mətn")
    
    # Əsas Nəticə
    verilen_bal: float = Field(..., ge=0, le=1)
    serh: str
    confidence_score: float
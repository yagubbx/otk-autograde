from pydantic import BaseModel, Field
from typing import Optional

# 1. OTK Bazasından BİZƏ GƏLƏCƏK məlumatın formatı (Giriş)
class EvaluationRequest(BaseModel):
    sual_id: str = Field(..., description="Sualın unikal kodu (məs: inf_001)")
    sual_metni: str
    duzgun_hell: str
    meyarlar: str
    sagird_id: str
    
    # Şagirdin həlli ya base64 formatında şəkil, ya da mətn ola bilər (ikisi də məcburi deyil, amma biri olmalıdır)
    sagird_helli_base64: Optional[str] = Field(None, description="Şagirdin şəkli (Base64 formatında)")
    sagird_helli_text: Optional[str] = Field(None, description="Şagirdin cavabı (Mətn formatında)")

# 2. Bizim AI-ın OTK-ya QAYTARACAĞI məlumatın formatı (Çıxış)
class EvaluationResponse(BaseModel):
    sagird_id: str
    sual_id: str
    # Ən vacib süzgəc: Bal YALNIZ 0 ilə 1 arasında ola bilər!
    verilen_bal: float = Field(..., ge=0, le=1, description="AI-ın verdiyi bal (0, 0.5, 1)")
    serh: str = Field(..., description="Balın verilmə səbəbi (AI şərhi)")
    confidence_score: float = Field(..., ge=0, le=1, description="AI-ın özünə inam dərəcəsi")
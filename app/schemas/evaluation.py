# app/schemas/evaluation.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional


# ---------------------------------------------------------------------------
# İzin verilən bal dəyərləri
# Standart: 0, 0.5, 1
# Bəzi fənlər üçün: 1/3 ≈ 0.333..., 2/3 ≈ 0.666...
# Hamısı 4 onluq rəqəmə qədər yuvarlaqlaşdırılır ki, float müqayisəsi
# etibarlı olsun (məs: 0.3333333... → 0.3333)
# ---------------------------------------------------------------------------
ALLOWED_SCORES = {
    round(0,        4),   # 0.0
    round(1/3,      4),   # 0.3333
    round(0.5,      4),   # 0.5
    round(2/3,      4),   # 0.6667
    round(1,        4),   # 1.0
}


# ---------------------------------------------------------------------------
# 1. GİRİŞ — İstifadəçidən / sistemdən gələn məlumat
# ---------------------------------------------------------------------------
class EvaluationRequest(BaseModel):
    sual_id:   str
    sagird_id: str

    # SUAL — ya mətn, ya şəkil, ya ikisi birlikdə
    sual_metni:        Optional[str] = None
    sual_sekli_base64: Optional[str] = None

    # DÜZGÜN HƏLL — ya mətn, ya şəkil, ya ikisi birlikdə
    duzgun_hell:             Optional[str] = None
    duzgun_hell_sekli_base64: Optional[str] = None

    # MEYARLAR — ya mətn, ya şəkil, ya ikisi birlikdə
    meyarlar:             Optional[str] = None
    meyarlar_sekli_base64: Optional[str] = None

    # ŞAGİRDİN HƏLLİ — ya mətn (online imtahan), ya şəkil (eyni imtahan skanı)
    sagird_helli_text:   Optional[str] = None
    sagird_helli_base64: Optional[str] = None


# ---------------------------------------------------------------------------
# 2. ÇIXIŞ — UI-a və sistemə qayıdan nəticə
# ---------------------------------------------------------------------------
class EvaluationResponse(BaseModel):
    sagird_id: str
    sual_id:   str

    # OCR mərhələsinin izahları (şəffaflıq üçün, UI-da göstərilə bilər)
    sualin_analizi:  Optional[str] = Field(
        None,
        description="AI-ın sual/düzgün həll/meyar şəkillərindən çıxardığı mətn"
    )
    sagirdin_analizi: Optional[str] = Field(
        None,
        description="AI-ın şagirdin əl yazısı şəklindən oxuduğu mətn"
    )

    # ── Əsas nəticə ────────────────────────────────────────────────────────
    verilen_bal:      float = Field(..., ge=0, le=1)
    serh:             str
    confidence_score: float = Field(..., ge=0, le=1)

    # ── Validation ─────────────────────────────────────────────────────────
    @field_validator("verilen_bal")
    @classmethod
    def bal_icaze_verilmis_deyerde_olmalidir(cls, v: float) -> float:
        """
        AI-dan gələn bal dəyərini yoxlayır.
        İzin verilənlər: 0 | 1/3 (≈0.3333) | 0.5 | 2/3 (≈0.6667) | 1

        Niyə yuvarlaqlaşdırma edirik:
          AI bəzən 0.33333333 və ya 0.6666666 qaytara bilər.
          4 onluq rəqəmə yuvarlaqlaşdırıb ALLOWED_SCORES ilə müqayisə edirik.
          Əgər yenə uyğun gəlməsə, xəta atırıq — sistem "istədiyi balı" uydurmur.
        """
        rounded = round(v, 4)
        if rounded not in ALLOWED_SCORES:
            allowed_str = " | ".join(str(s) for s in sorted(ALLOWED_SCORES))
            raise ValueError(
                f"Verilən bal '{v}' icazə verilmir. "
                f"İcazə verilən dəyərlər: {allowed_str}"
            )
        return rounded
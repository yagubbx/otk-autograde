# app/services/ai/openai_provider.py
import os
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Asinxron OpenAI müştərisini başladırıq
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------------------------------------------------------
# HAKİM AGENTİN ÇIXIŞ SXEMİ (STRUCTURED OUTPUT ÜÇÜN)
# AI yalnız bu üç dəyəri düşünəcək və tam bu strukturda OBYEKT qaytaracaq
# ---------------------------------------------------------------------------
class JudgeOutput(BaseModel):
    verilen_bal: float = Field(
        description="Şagirdin topladığı yekun bal (yalnız meyardakı icazə verilən rəqəmlər: 0, 0.3333, 0.5, 0.6667, 1)"
    )
    serh: str = Field(
        description="Şagirdin hansı meyarı ödəyib/ödəmədiyi barədə sərt müəllim şərhi"
    )
    confidence_score: float = Field(
        description="AI-ın bu qərardakı əminlik dərəcəsi (0.0 ilə 1.0 arasında)"
    )

class OpenAIProvider:
    
    # -----------------------------------------------------------------------
    # 1. GÖZ AGENTİ (VISION) - Yalnız oxuyur və MƏTN (String) qaytarır
    # -----------------------------------------------------------------------
    @staticmethod
    async def call_vision_agent(messages: list) -> str:
        """
        Şəkilləri OCR və Semantik Bərpa üçün OpenAI Vision modelinə göndərir.
        Burada klassik '.create' istifadə edirik, çünki bizə sadəcə Markdown/Mətn lazımdır.
        """
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",  # Vision dəstəkləyən model
                messages=messages,
                temperature=0.0, # Uydurmanın (Hallüsinasiyanın) qarşısını almaq üçün 0.0
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Göz Agenti (Vision) xətası: {str(e)}")

    # -----------------------------------------------------------------------
    # 2. HAKİM AGENT (JUDGE) - Qiymətləndirir və OBYEKT (Pydantic) qaytarır
    # -----------------------------------------------------------------------
    @staticmethod
    async def call_judge_agent(messages: list) -> JudgeOutput:
        """
        Hakim Agent üçün STRUCTURED OUTPUTS (beta.parse) zəngi.
        Bu metod string YOX, birbaşa yoxlanılmış Pydantic obyekti (JudgeOutput) qaytarır!
        JSONDecodeError ehtimalı tamamilə SIFIRDIR.
        """
        try:
            # SEHR BURADADIR: client.beta.chat.completions.parse
            response = await client.beta.chat.completions.parse(
                model="gpt-4o", # Structured Outputs gpt-4o və gpt-4o-mini-də dəstəklənir
                messages=messages,
                response_format=JudgeOutput,
                temperature=0.0 # Maksimum obyektivlik və dəqiqlik
            )
            
            # Obyekt artıq AI tərəfindən tam doldurulub və validasiya edilib
            # Bizə birbaşa Python obyekti (JudgeOutput) qayıdır
            return response.choices[0].message.parsed
        
        except Exception as e:
            raise Exception(f"Hakim Agent xətası: {str(e)}")
# app/services/ai/providers/openai_provider.py
from openai import AsyncOpenAI
import json
from app.core.config import settings
from app.schemas.evaluation import EvaluationResponse

class OpenAIProvider:
    def __init__(self):
        # Asinxron klient yaradırıq (Sürət üçün)
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o" # Vision (şəkil oxuma) dəstəkləyən model

    async def evaluate_submission(self, system_prompt: str, user_content: list) -> EvaluationResponse:
        """
        AI-ya sorğu göndərir və nəticəni Pydantic modelinə çevirib qaytarır.
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.0, # ÇOX VACİB: Hallucination-u sıfıra endirir, stabil cavab verir
                max_tokens=500,
                response_format={ "type": "json_object" } # AI-ı JSON qaytarmağa məcbur edir
            )
            
            # AI-dan gələn xam (raw) mətni alırıq
            raw_response = response.choices[0].message.content
            
            # Mətni JSON obyektinə çeviririk (Dictionary)
            json_data = json.loads(raw_response)
            
            # Bura bir az "hiylədir". Pydantic modelimizi (EvaluationResponse)
            # yaratmaq üçün saxta ID-lər qoyuruq. Əsl ID-ləri Orchestrator təyin edəcək.
            return EvaluationResponse(
                sagird_id="temp",
                sual_id="temp",
                verilen_bal=json_data.get("verilen_bal", 0.0),
                serh=json_data.get("serh", "Şərh yoxdur"),
                confidence_score=json_data.get("confidence_score", 0.8)
            )
            
        except Exception as e:
            # Əgər API çökərsə və ya pul bitərsə, sistem çökməsin deyə xəta atırıq
            raise ValueError(f"OpenAI xətası baş verdi: {str(e)}")
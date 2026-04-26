# app/services/orchestrator/evaluation_flow.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.evaluation import EvaluationRequest, EvaluationResponse
from app.services.ai.prompt_builder import PromptBuilder
from app.services.ai.providers.openai_provider import OpenAIProvider
from app.db.models import Evaluation
import uuid
import json

async def run_evaluation_flow(request: EvaluationRequest, db: AsyncSession) -> EvaluationResponse:
    """
    Sistemin bütün prosesini idarə edən mərkəzi funksiya.
    """
    # 1. Promptları Qururuq
    system_prompt = PromptBuilder.build_judge_prompt(
        sual_metni=request.sual_metni,
        duzgun_hell=request.duzgun_hell,
        meyarlar=request.meyarlar
    )
    user_message = PromptBuilder.build_user_message(
        sagird_helli_text=request.sagird_helli_text,
        sagird_helli_image=request.sagird_helli_base64
    )

    # 2. AI Modelinə Göndəririk
    ai_provider = OpenAIProvider()
    ai_result = await ai_provider.evaluate_submission(system_prompt, user_message)

    # 3. Yekun Nəticəni Hazırlayırıq (ID-ləri yerinə qoyuruq)
    ai_result.sagird_id = request.sagird_id
    ai_result.sual_id = request.sual_id
    evaluation_id = f"eval_{uuid.uuid4().hex[:8]}" # Unikal ID yaradırıq

    # 4. Məlumatları Audit üçün Verilənlər Bazasında Saxlayırıq
    new_evaluation = Evaluation(
        id=evaluation_id,
        sual_id=request.sual_id,
        sagird_id=request.sagird_id,
        sagird_helli=request.sagird_helli_text or "Şəkil göndərilib",
        verilen_bal=ai_result.verilen_bal,
        serh=ai_result.serh,
        confidence_score=ai_result.confidence_score,
        # AI-ın verdiyi JSON-u bazaya text kimi yazırıq ki, gələcəkdə baxaq
        raw_ai_response=ai_result.model_dump_json() 
    )
    
    db.add(new_evaluation)
    await db.commit() # Bazaya yaz!

    # 5. Cavabı API-yə Qaytarırıq
    return ai_result
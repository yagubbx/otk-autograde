# app/services/orchestrator/evaluation_flow.py
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.schemas.evaluation import EvaluationRequest, EvaluationResponse
from app.db.models import Question, Evaluation
from app.services.ai.openai_provider import OpenAIProvider
from app.services.ai.prompt_builder import PromptBuilder

async def run_evaluation_flow(request: EvaluationRequest, db: AsyncSession) -> EvaluationResponse:
    
    # Köməkçi funksiya: Şəkli oxumaq üçün Vision Agentə müraciət
    async def get_vision_text(image_b64: str) -> str:
        messages = [
            {"role": "system", "content": PromptBuilder.build_vision_transcriber_prompt()},
            {"role": "user", "content": [
                {"type": "text", "text": "Bu şəkildəki məlumatı qadağalara və qaydalara qəti əməl edərək mətnə çevir:"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}", "detail": "high"}}
            ]}
        ]
        return await OpenAIProvider.call_vision_agent(messages)

    # ----------------------------------------------------------------------
    # 1. MƏRHƏLƏ: SUALIN KEŞLƏNMƏSİ VƏ YA ANALİZİ (TOKEN QƏNAƏTİ)
    # ----------------------------------------------------------------------
    result = await db.execute(select(Question).where(Question.id == request.sual_id))
    question_db = result.scalar_one_or_none()
    
    sualin_analizi_log = "" 
    
    if not question_db or not question_db.is_processed:
        sualin_analizi_log += "Sual bazada tapılmadı. Yeni analiz başladılır...\n"
        
        # Sualın Şərti
        yekun_sual = request.sual_metni or ""
        if request.sual_sekli_base64:
            sualin_analizi_log += "- Sualın şəkli OCR edilir...\n"
            sual_ocr = await get_vision_text(request.sual_sekli_base64)
            yekun_sual += f"\n[Şəkildən Oxunan Sual]:\n{sual_ocr}"
            
        # Düzgün Həll
        yekun_hell = request.duzgun_hell or ""
        if request.duzgun_hell_sekli_base64:
            sualin_analizi_log += "- Düzgün həllin şəkli OCR edilir...\n"
            hell_ocr = await get_vision_text(request.duzgun_hell_sekli_base64)
            yekun_hell += f"\n[Şəkildən Oxunan Həll]:\n{hell_ocr}"
            
        # Meyarlar
        yekun_meyar = request.meyarlar or ""
        if request.meyarlar_sekli_base64:
            sualin_analizi_log += "- Meyarların şəkli OCR edilir...\n"
            meyar_ocr = await get_vision_text(request.meyarlar_sekli_base64)
            yekun_meyar += f"\n[Şəkildən Oxunan Meyarlar]:\n{meyar_ocr}"
        
        # Baza Qeydiyyatı
        if not question_db:
            question_db = Question(id=request.sual_id)
            db.add(question_db)
            
        question_db.sual_metni = yekun_sual
        question_db.duzgun_hell = yekun_hell
        question_db.meyarlar = yekun_meyar
        question_db.processed_context = f"SUAL:\n{yekun_sual}\nHƏLL:\n{yekun_hell}\nMEYAR:\n{yekun_meyar}"
        question_db.is_processed = True
        
        await db.commit()
        await db.refresh(question_db)
        sualin_analizi_log += "✅ Analiz bitdi və məlumatlar bazada keşləndi."
    else:
        sualin_analizi_log = "⚡ Bu sual əvvəldən analiz edilib. Məlumatlar birbaşa bazadan sürətlə çəkildi (0 Token xərcləndi)."

    # ----------------------------------------------------------------------
    # 2. MƏRHƏLƏ: ŞAGİRDİN CAVABININ OXUNMASI ("GÖZ" AGENTİ)
    # ----------------------------------------------------------------------
    yekun_sagird_helli = request.sagird_helli_text or ""
    sagirdin_analizi_log = ""
    
    if request.sagird_helli_base64:
        sagird_ocr = await get_vision_text(request.sagird_helli_base64)
        yekun_sagird_helli += f"\n[Şagirdin Əl Yazmasından Oxunanlar]:\n{sagird_ocr}"
        sagirdin_analizi_log = sagird_ocr 
    else:
        sagirdin_analizi_log = "Şəkil göndərilməyib. Yalnız mətn yoxlanılır."

    # ----------------------------------------------------------------------
    # 3. MƏRHƏLƏ: QİYMƏTLƏNDİRMƏ ("HAKİM" AGENTİ - STRUCTURED OUTPUT)
    # ----------------------------------------------------------------------
    system_prompt = PromptBuilder.build_judge_prompt(
        sual_metni=question_db.sual_metni,
        duzgun_hell=question_db.duzgun_hell,
        meyarlar=question_db.meyarlar
    )
    
    user_content = PromptBuilder.build_user_message(sagird_helli_text=yekun_sagird_helli)
    
    # Hakim Agent üçün mesajların hazırlanması
    judge_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]
    
    # 🔥 SEHR BURADADIR: judge_output artıq JSON text deyil, birbaşa "JudgeOutput" obyektidir!
    judge_output = await OpenAIProvider.call_judge_agent(judge_messages)

    # ----------------------------------------------------------------------
    # 4. MƏRHƏLƏ: AUDİT VƏ NƏTİCƏNİN QAYTARILMASI
    # ----------------------------------------------------------------------
    evaluation_id = f"eval_{uuid.uuid4().hex[:8]}"
    
    new_evaluation = Evaluation(
        id=evaluation_id,
        sual_id=request.sual_id,
        sagird_id=request.sagird_id,
        sagird_helli_original=request.sagird_helli_text or "[Şəkil yüklənib]",
        sagird_helli_transkripsiya=yekun_sagird_helli, 
        verilen_bal=judge_output.verilen_bal,
        serh=judge_output.serh,
        confidence_score=judge_output.confidence_score,
        raw_ai_response=judge_output.model_dump_json() # Obyekti bazaya yazmaq üçün JSON-a çeviririk
    )
    
    db.add(new_evaluation)
    await db.commit()

    # Yekun Cavabı (EvaluationResponse sxeminə uyğun) qaytarırıq
    return EvaluationResponse(
        sual_id=request.sual_id,
        sagird_id=request.sagird_id,
        sualin_analizi=sualin_analizi_log,
        sagirdin_analizi=sagirdin_analizi_log,
        verilen_bal=judge_output.verilen_bal,
        serh=judge_output.serh,
        confidence_score=judge_output.confidence_score
    )
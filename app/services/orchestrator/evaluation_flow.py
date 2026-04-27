# app/services/orchestrator/evaluation_flow.py
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas.evaluation import EvaluationRequest, EvaluationResponse
from app.db.models import Question, Evaluation
from app.services.ai.providers.openai_provider import OpenAIProvider
from app.services.ai.prompt_builder import PromptBuilder

async def run_evaluation_flow(request: EvaluationRequest, db: AsyncSession) -> EvaluationResponse:
    ai_provider = OpenAIProvider()
    
    # ----------------------------------------------------------------------
    # 1. MƏRHƏLƏ: SUALIN KEŞLƏNMƏSİ VƏ YA ANALİZİ (TOKEN QƏNAƏTİ)
    # ----------------------------------------------------------------------
    # Əvvəlcə baxırıq: Bu sual bazamızda artıq analiz edilibmi?
    result = await db.execute(select(Question).where(Question.id == request.sual_id))
    question_db = result.scalar_one_or_none()
    
    sualin_analizi_log = "" # UI-da göstərmək üçün
    
    # Əgər sual bazada yoxdursa və ya hələ emal edilməyibsə:
    if not question_db or not question_db.is_processed:
        sualin_analizi_log += "Sual bazada tapılmadı. Yeni analiz başladılır...\n"
        
        # Sualın Şərti (Şəkil varsa oxu, mətnlə birləşdir)
        yekun_sual = request.sual_metni or ""
        if request.sual_sekli_base64:
            sualin_analizi_log += "- Sualın şəkli OCR edilir...\n"
            sual_ocr = await ai_provider.extract_text_from_image(
                PromptBuilder.build_vision_transcriber_prompt(), request.sual_sekli_base64
            )
            yekun_sual += f"\n[Şəkildən Oxunan Sual]:\n{sual_ocr}"
            
        # Düzgün Həll (Şəkil varsa oxu, mətnlə birləşdir)
        yekun_hell = request.duzgun_hell or ""
        if request.duzgun_hell_sekli_base64:
            sualin_analizi_log += "- Düzgün həllin şəkli OCR edilir...\n"
            hell_ocr = await ai_provider.extract_text_from_image(
                PromptBuilder.build_vision_transcriber_prompt(), request.duzgun_hell_sekli_base64
            )
            yekun_hell += f"\n[Şəkildən Oxunan Həll (Məs: Blok sxem)]:\n{hell_ocr}"
            
        # Meyarlar (Şəkil varsa oxu, mətnlə birləşdir)
        yekun_meyar = request.meyarlar or ""
        if request.meyarlar_sekli_base64:
            sualin_analizi_log += "- Meyarların şəkli OCR edilir...\n"
            meyar_ocr = await ai_provider.extract_text_from_image(
                PromptBuilder.build_vision_transcriber_prompt(), request.meyarlar_sekli_base64
            )
            yekun_meyar += f"\n[Şəkildən Oxunan Meyarlar]:\n{meyar_ocr}"
        
        # Baza Qeydiyyatı (Əgər heç yoxdursa, yeni sətir yarat)
        if not question_db:
            question_db = Question(id=request.sual_id)
            db.add(question_db)
            
        # Məlumatları bazaya yaz və "Keşləndi" (is_processed=True) olaraq işarələ
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
        # Şagird şəkli HƏMİŞƏ oxunmalıdır (Çünki hər şagirdin cavabı unikaldır)
        sagird_ocr = await ai_provider.extract_text_from_image(
            PromptBuilder.build_vision_transcriber_prompt(), request.sagird_helli_base64
        )
        yekun_sagird_helli += f"\n[Şagirdin Əl Yazmasından Oxunanlar]:\n{sagird_ocr}"
        sagirdin_analizi_log = sagird_ocr # Sırf ekranda göstərmək üçün
    else:
        sagirdin_analizi_log = "Şəkil göndərilməyib. Yalnız mətn yoxlanılır."

    # ----------------------------------------------------------------------
    # 3. MƏRHƏLƏ: QİYMƏTLƏNDİRMƏ ("HAKİM" AGENTİ)
    # ----------------------------------------------------------------------
    # Fikir ver: Hakimə göndərilən məlumatlar artıq birbaşa BAZADAN (question_db) gəlir.
    system_prompt = PromptBuilder.build_judge_prompt(
        sual_metni=question_db.sual_metni,
        duzgun_hell=question_db.duzgun_hell,
        meyarlar=question_db.meyarlar
    )
    
    # Şagirdin "təmizlənmiş" mətni Hakimə gedir
    user_message = PromptBuilder.build_user_message(sagird_helli_text=yekun_sagird_helli)
    
    # Hakim AI yekun qərarı verir
    ai_result = await ai_provider.evaluate_submission(system_prompt, user_message)

    # ----------------------------------------------------------------------
    # 4. MƏRHƏLƏ: AUDİT VƏ NƏTİCƏNİN QAYTARILMASI
    # ----------------------------------------------------------------------
    evaluation_id = f"eval_{uuid.uuid4().hex[:8]}"
    
    new_evaluation = Evaluation(
        id=evaluation_id,
        sual_id=request.sual_id,
        sagird_id=request.sagird_id,
        sagird_helli_original=request.sagird_helli_text or "[Şəkil yüklənib]",
        sagird_helli_transkripsiya=yekun_sagird_helli, # Sənin üçün sübut məqsədli
        verilen_bal=ai_result.verilen_bal,
        serh=ai_result.serh,
        confidence_score=ai_result.confidence_score,
        raw_ai_response=ai_result.model_dump_json()
    )
    
    db.add(new_evaluation)
    await db.commit()

    # Nəticəni UI-a qaytararkən oxunmuş analizləri də əlavə edirik
    ai_result.sagird_id = request.sagird_id
    ai_result.sual_id = request.sual_id
    ai_result.sualin_analizi = sualin_analizi_log
    ai_result.sagirdin_analizi = sagirdin_analizi_log

    return ai_result
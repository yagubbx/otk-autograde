# app/api/v1/endpoints.py
import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.evaluation import EvaluationRequest, EvaluationResponse
from app.db.session import get_db
from app.services.orchestrator.evaluation_flow import run_evaluation_flow

router = APIRouter()

# 1. FƏRDİ (TƏK) YOXLAMA ENDPOINTİ
@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_submission(request: EvaluationRequest, db: AsyncSession = Depends(get_db)):
    """
    Şagirdin həllini qəbul edir, AI ilə yoxlayır, bazaya yazır və balı qaytarır.
    """
    try:
        return await run_evaluation_flow(request, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fərdi yoxlama zamanı xəta: {str(e)}")

# 2. KÜTLƏVİ (PARALEL) YOXLAMA ENDPOINTİ
@router.post("/evaluate/batch", response_model=List[EvaluationResponse])
async def evaluate_batch_submissions(requests: List[EvaluationRequest], db: AsyncSession = Depends(get_db)):
    """
    Birdən çox şagirdin cavabını alır və ASİNXRON olaraq (eyni anda) yoxlayır.
    """
    try:
        # asyncio.gather -> Bütün tapşırıqları eyni anda OpenAI-a atır və paralel gözləyir. Sürət sirri budur!
        tasks = [run_evaluation_flow(req, db) for req in requests]
        results = await asyncio.gather(*tasks)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kütləvi yoxlama zamanı xəta: {str(e)}")
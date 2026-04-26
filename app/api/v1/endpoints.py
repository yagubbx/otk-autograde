# app/api/v1/endpoints.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.evaluation import EvaluationRequest, EvaluationResponse
from app.db.session import get_db
from app.services.orchestrator.evaluation_flow import run_evaluation_flow

router = APIRouter()

@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_submission_endpoint(
    request: EvaluationRequest, 
    db: AsyncSession = Depends(get_db)
):
    """
    Şagirdin həllini qəbul edir, AI ilə yoxlayır, bazaya yazır və balı qaytarır.
    """
    # Gələn sorğunu birbaşa Dirijora veririk
    return await run_evaluation_flow(request, db)
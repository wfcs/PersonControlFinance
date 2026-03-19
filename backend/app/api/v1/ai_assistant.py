from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.plan_limits import get_plan_limits
from app.db.session import get_session
from app.models.user import User
from app.schemas.ai_assistant import AiAnswer, AiQuestion
from app.services.ai_service import answer_question

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.post("/ask", response_model=AiAnswer)
async def ask(
    data: AiQuestion,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> AiAnswer:
    """Ask the AI financial assistant a question (premium feature)."""
    plan = get_plan_limits(current_user.tenant.plan)
    if "ai_assistant" not in plan.features:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI Assistant requires a Premium plan.",
        )

    answer = await answer_question(data.question, current_user.tenant_id, session)
    return AiAnswer(question=data.question, answer=answer)

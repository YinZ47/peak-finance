"""AI advisor routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User, Expense, DebtAccount, Goal
from app.schemas import AIAskRequest, AIInsight
from app.security import get_current_user
from app.services.ai import (
    AIProvider,
    build_user_context,
    classify_intent,
    is_intent_allowed,
    redact_pii_from_message
)
from app.services.audit import log_action
from app.services.compliance import get_ai_meta
from app.settings import settings

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/ask", response_model=AIInsight)
def ask_ai(
    request: AIAskRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
) -> AIInsight:
    """Provide educational financial guidance using the AI advisor."""

    intent = classify_intent(request.question)
    allowed = is_intent_allowed(intent, settings.IS_REGULATED_PARTNER)

    expenses = db.query(Expense).filter(Expense.user_id == user.id).all()
    debts = db.query(DebtAccount).filter(DebtAccount.user_id == user.id).all()
    goals = db.query(Goal).filter(Goal.user_id == user.id).all()
    ai_rules = user.ai_rules  # may be None

    meta = get_ai_meta()
    meta.update({
        "intent": intent.value,
        "regulated_mode": settings.IS_REGULATED_PARTNER
    })

    if not allowed:
        answer = (
            "This request needs regulated capabilities (loan approval, e-KYC, or CIB access). "
            "Peak Finance operates in educational mode, so we cannot process it."
        )

        log_action(
            db,
            "ai_request_blocked",
            user,
            {
                "intent": intent.value,
                "question": redact_pii_from_message(request.question)
            }
        )

        return AIInsight(
            answer=answer,
            intent=intent.value,
            is_blocked=True,
            meta=meta
        )

    provider = AIProvider()
    context = build_user_context(user, expenses, debts, goals, ai_rules)
    answer = provider.generate_response(request.question, context)

    meta.update({
        "provider": provider.active_provider,
        "context_summary": context
    })

    log_action(
        db,
        "ai_request_answered",
        user,
        {
            "intent": intent.value,
            "question": redact_pii_from_message(request.question),
            "provider": meta["provider"]
        }
    )

    return AIInsight(
        answer=answer,
        intent=intent.value,
        is_blocked=False,
        meta=meta
    )

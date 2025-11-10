"""AI advisor service with provider abstraction and guardrails."""
from typing import List, Optional
from enum import Enum
from app.settings import settings
from app.models import User, AIRule
from app.services.calculators import fun_budget
from app.schemas import AIInsight


class IntentCategory(str, Enum):
    """AI message intent categories."""
    GENERAL_ADVICE = "general_advice"
    BUDGET_HELP = "budget_help"
    LOAN_QUESTION = "loan_question"
    GOAL_PLANNING = "goal_planning"
    SPENDING_QUERY = "spending_query"
    LOAN_APPROVAL_REQUEST = "loan_approval_request"  # BLOCKED
    EKYC_REQUEST = "ekyc_request"  # BLOCKED
    CIB_ACCESS_REQUEST = "cib_access_request"  # BLOCKED
    UNKNOWN = "unknown"


# Blocked intents (regulated features)
BLOCKED_INTENTS = {
    IntentCategory.LOAN_APPROVAL_REQUEST,
    IntentCategory.EKYC_REQUEST,
    IntentCategory.CIB_ACCESS_REQUEST
}


class AIProvider:
    """AI provider abstraction (Hugging Face, OpenAI-compatible, or mock)."""

    def __init__(self):
        self.provider = (settings.AI_PROVIDER or "openai").lower().strip()
        self.base_url = settings.AI_BASE_URL
        self.model = settings.AI_MODEL
        self.api_key = settings.AI_API_KEY
        self.system_prompt = settings.AI_SYSTEM_PROMPT.strip()
        if self.provider == "huggingface":
            self.is_configured = bool(self.api_key and self.model)
        else:
            self.is_configured = bool(self.api_key and self.model)
        self.active_provider = self.provider if self.is_configured else "mock"
    
    def generate_response(self, prompt: str, context: str) -> str:
        """
        Generate AI response.
        
        Args:
            prompt: User message
            context: User financial context
            
        Returns:
            AI-generated response
        """
        if not self.is_configured:
            return self._mock_response(prompt, context)

        if self.provider == "huggingface":
            return self._call_huggingface(prompt, context)

        return self._call_openai(prompt, context)

    def _call_openai(self, prompt: str, context: str) -> str:
        """Call OpenAI-compatible API."""
        try:
            from openai import OpenAI

            client_kwargs = {
                "api_key": self.api_key,
                "timeout": settings.AI_TIMEOUT,
                "max_retries": settings.AI_MAX_RETRIES
            }

            if self.base_url:
                client_kwargs["base_url"] = self.base_url

            client = OpenAI(**client_kwargs)

            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {prompt}"}
            ]

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"AI service temporarily unavailable. Error: {str(e)}"
    
    def _call_huggingface(self, prompt: str, context: str) -> str:
        """Call Hugging Face Inference API using huggingface-hub client."""
        try:
            from huggingface_hub import InferenceClient  # type: ignore[import-not-found]

            client = InferenceClient(model=self.model, token=self.api_key)

            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": (
                        "Provide the response as a short narrative with bullet points when helpful.\n\n"
                        f"Context:\n{context}\n\nQuestion:\n{prompt}"
                    )
                }
            ]

            result = client.chat_completion(
                messages=messages,
                max_tokens=400,
                temperature=0.6,
                top_p=0.9
            )

            if not getattr(result, "choices", None):
                return "AI service responded without content. Please try again shortly."

            message = result.choices[0].message
            if isinstance(message, dict):
                content = message.get("content", "").strip()
            else:
                content = getattr(message, "content", "").strip()

            return content or "AI service responded without content. Please try again shortly."

        except ImportError:
            return (
                "Hugging Face client is not installed. Run 'pip install huggingface-hub' "
                "and restart the service."
            )
        except Exception as e:
            return f"AI service temporarily unavailable. Error: {str(e)}"

    def _mock_response(self, prompt: str, context: str) -> str:
        """Generate deterministic mock response."""
        prompt_lower = prompt.lower()
        
        # Pattern matching for common queries
        if any(word in prompt_lower for word in ['budget', 'spend', 'expense']):
            return (
                "Based on your current financial situation, here's some guidance:\n\n"
                "1. Track all expenses (fixed and variable)\n"
                "2. Aim to keep essential expenses below 50% of income\n"
                "3. Allocate 20% to savings and goals\n"
                "4. Keep discretionary spending around 15-20%\n\n"
                "Your current safe-to-spend amount is calculated by: "
                "Balance - Bills - Debt Minimums - Reserve - Goal Allocations\n\n"
                "This is educational guidance. Please consult a financial advisor for personalized advice."
            )
        
        elif any(word in prompt_lower for word in ['loan', 'debt', 'emi']):
            return (
                "When considering a loan:\n\n"
                "1. Keep your DTI (Debt-to-Income) ratio below 40%\n"
                "2. EMI formula: P × r × (1+r)^n / ((1+r)^n - 1)\n"
                "   Where P=principal, r=monthly rate, n=months\n"
                "3. Compare offers from multiple lenders\n"
                "4. Consider stress scenarios (+2% rate, -10% income)\n\n"
                "Use our loan calculator for estimates. Remember: estimates are illustrative; "
                "approval and terms are set by licensed lenders.\n\n"
                "This is educational information, not a loan offer."
            )
        
        elif any(word in prompt_lower for word in ['goal', 'save', 'saving']):
            return (
                "Tips for reaching your financial goals:\n\n"
                "1. Set specific, measurable targets with deadlines\n"
                "2. Automate savings (pay yourself first)\n"
                "3. Prioritize goals (emergency fund → debt → long-term)\n"
                "4. Review progress monthly and adjust as needed\n\n"
                "Track your goals in the Goals section. We'll help monitor your progress!\n\n"
                "This is educational guidance based on your inputs."
            )
        
        else:
            return (
                "I'm here to help with:\n"
                "• Budget planning and expense tracking\n"
                "• Loan affordability estimates (educational)\n"
                "• Inflation projections for essential expenses\n"
                "• Goal setting and savings strategies\n\n"
                "What would you like to know more about?\n\n"
                "Note: This is educational guidance, not professional financial advice."
            )


def classify_intent(message: str) -> IntentCategory:
    """
    Classify user message intent.
    
    Args:
        message: User message
        
    Returns:
        Intent category
    """
    msg_lower = message.lower()
    
    # Check for blocked intents first
    if any(word in msg_lower for word in ['approve', 'approval', 'grant loan', 'give me loan']):
        return IntentCategory.LOAN_APPROVAL_REQUEST
    
    if any(word in msg_lower for word in ['ekyc', 'e-kyc', 'kyc', 'verify identity', 'id verification']):
        return IntentCategory.EKYC_REQUEST
    
    if any(word in msg_lower for word in ['cib', 'credit bureau', 'credit report', 'credit score']):
        return IntentCategory.CIB_ACCESS_REQUEST
    
    # Allowed intents
    if any(word in msg_lower for word in ['budget', 'expense', 'spend']):
        return IntentCategory.BUDGET_HELP
    
    if any(word in msg_lower for word in ['loan', 'emi', 'debt', 'borrow']):
        return IntentCategory.LOAN_QUESTION
    
    if any(word in msg_lower for word in ['goal', 'save', 'saving']):
        return IntentCategory.GOAL_PLANNING
    
    if any(word in msg_lower for word in ['safe to spend', 'can i spend', 'afford']):
        return IntentCategory.SPENDING_QUERY
    
    if any(word in msg_lower for word in ['advice', 'help', 'suggest']):
        return IntentCategory.GENERAL_ADVICE
    
    return IntentCategory.UNKNOWN


def is_intent_allowed(intent: IntentCategory, is_regulated: bool) -> bool:
    """
    Check if intent is allowed given feature flags.
    
    Args:
        intent: Classified intent
        is_regulated: Whether app is in regulated mode
        
    Returns:
        True if allowed, False otherwise
    """
    # Blocked intents are never allowed in educational mode
    if intent in BLOCKED_INTENTS and not is_regulated:
        return False
    return True


def build_user_context(
    user: User,
    expenses: List,
    debts: List,
    goals: List,
    ai_rules: Optional[AIRule]
) -> str:
    """
    Build context summary for AI.
    
    Args:
        user: User object
        expenses: List of expenses
        debts: List of debts
        goals: List of goals
        ai_rules: AI rules if any
        
    Returns:
        Context string
    """
    total_expenses = sum(e.amount for e in expenses)
    total_debt_emi = sum(d.current_emi for d in debts)
    total_goal_targets = sum(g.target_amount for g in goals)
    total_goal_saved = sum(g.saved_amount for g in goals)
    
    fun_ratio = ai_rules.fun_ratio if ai_rules else settings.DEFAULT_FUN_RATIO
    fun_budget_amt = fun_budget(user.monthly_net_income, fun_ratio)
    
    context = f"""
User Financial Summary:
- Monthly Income: ৳{user.monthly_net_income:,.2f}
- Total Monthly Expenses: ৳{total_expenses:,.2f}
- Total Monthly Debt Payments (EMI): ৳{total_debt_emi:,.2f}
- Surplus: ৳{user.monthly_net_income - total_expenses - total_debt_emi:,.2f}
- Fun Budget Allocation: ৳{fun_budget_amt:,.2f} ({fun_ratio*100:.0f}% of income)
- Goals: {len(goals)} active (Target: ৳{total_goal_targets:,.2f}, Saved: ৳{total_goal_saved:,.2f})
- Risk Tolerance: {user.risk_tolerance or 'Not set'}
"""
    return context.strip()


def generate_insights(
    user: User,
    expenses: List,
    debts: List,
    goals: List,
    ai_rules: Optional[AIRule]
) -> List[AIInsight]:
    """
    Generate AI insights based on user data.
    
    Args:
        user: User object
        expenses: List of expenses
        debts: List of debts
        goals: List of goals
        ai_rules: AI rules if any
        
    Returns:
        List of insights
    """
    insights: List[AIInsight] = []
    
    total_expenses = sum(e.amount for e in expenses)
    total_debt_emi = sum(d.current_emi for d in debts)
    surplus = user.monthly_net_income - total_expenses - total_debt_emi
    
    # Insight 1: Surplus/deficit
    if surplus < 0:
        insights.append(AIInsight(
            type="budget",
            title="⚠️ Budget Deficit",
            message=f"You're spending ৳{abs(surplus):,.2f} more than you earn monthly. Consider reducing variable expenses.",
            severity="critical"
        ))
    elif surplus > 0:
        insights.append(AIInsight(
            type="budget",
            title="✅ Positive Cash Flow",
            message=f"You have a surplus of ৳{surplus:,.2f}/month. Great job! Consider allocating to goals or emergency fund.",
            severity="info"
        ))
    
    # Insight 2: DTI check
    if user.monthly_net_income > 0:
        dti_ratio = total_debt_emi / user.monthly_net_income
        if dti_ratio > 0.4:
            insights.append(AIInsight(
                type="debt",
                title="⚠️ High Debt-to-Income Ratio",
                message=f"Your DTI is {dti_ratio*100:.1f}% (recommended: <40%). Avoid taking new loans until DTI improves.",
                severity="warning"
            ))
    
    # Insight 3: Goal progress
    for goal in goals[:3]:  # Top 3 goals
        if goal.target_amount > 0:
            progress = (goal.saved_amount / goal.target_amount) * 100
            if progress < 25:
                insights.append(AIInsight(
                    type="goal",
                    title=f"📊 Goal: {goal.name}",
                    message=f"Only {progress:.1f}% complete. Increase monthly contributions to stay on track.",
                    severity="info"
                ))
    
    # Insight 4: Debt prepayment opportunity
    if surplus > total_debt_emi * 0.5 and debts:
        insights.append(AIInsight(
            type="debt",
            title="💡 Prepayment Opportunity",
            message=f"You could pay extra ৳{surplus * 0.2:,.2f}/month on debts to save on interest and finish early.",
            severity="info"
        ))
    
    return insights


def redact_pii_from_message(message: str) -> str:
    """
    Redact PII from AI messages before logging.
    
    Args:
        message: Message text
        
    Returns:
        Redacted message
    """
    from app.services.audit import redact_pii
    return redact_pii(message)
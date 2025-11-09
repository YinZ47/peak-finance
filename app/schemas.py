"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from app.models import RiskTolerance, ExpenseType, ConsentScope


# ============ AUTH ============
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    id: int
    email: str
    locale: str
    currency: str
    risk_tolerance: Optional[RiskTolerance]
    monthly_net_income: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    locale: Optional[str] = None
    currency: Optional[str] = None
    risk_tolerance: Optional[RiskTolerance] = None
    monthly_net_income: Optional[float] = Field(None, ge=0)


# ============ EXPENSES ============
class ExpenseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(..., ge=0)
    type: ExpenseType


class ExpenseResponse(BaseModel):
    id: int
    user_id: int
    name: str
    amount: float
    type: ExpenseType
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ DEBTS ============
class DebtCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    principal: float = Field(..., ge=0)
    annual_rate_pct: float = Field(..., ge=0)
    term_months: int = Field(..., ge=1)
    current_emi: float = Field(..., ge=0)


class DebtResponse(BaseModel):
    id: int
    user_id: int
    name: str
    principal: float
    annual_rate_pct: float
    term_months: int
    current_emi: float
    start_date: datetime
    
    class Config:
        from_attributes = True


# ============ GOALS ============
class GoalCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    target_amount: float = Field(..., ge=0)
    saved_amount: float = Field(default=0, ge=0)
    target_date: Optional[datetime] = None
    priority: int = Field(default=1, ge=1)


class GoalResponse(BaseModel):
    id: int
    user_id: int
    name: str
    target_amount: float
    saved_amount: float
    target_date: Optional[datetime]
    priority: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ CALCULATORS ============
class LoanPreAssessmentRequest(BaseModel):
    income: float = Field(..., gt=0)
    existing_monthly_debt: float = Field(..., ge=0)
    loan_type: str = Field(default="personal")
    term_months: int = Field(..., ge=1)
    annual_rate_pct: float = Field(..., ge=0)


class StressTestResult(BaseModel):
    scenario: str
    dti: float
    affordable_emi: float
    principal_est: float


class LoanPreAssessmentResponse(BaseModel):
    dti: float
    affordable_emi_cap: float
    principal_est: float
    stress_tests: List[StressTestResult]
    meta: Dict[str, str]


class LoanPayoffPlanRequest(BaseModel):
    principal: float = Field(..., ge=0)
    annual_rate_pct: float = Field(..., ge=0)
    months_remaining: int = Field(..., ge=1)


class LoanPayoffPlanResponse(BaseModel):
    required_emi: float
    total_interest: float
    total_payment: float
    meta: Dict[str, str]


class InflationItem(BaseModel):
    name: str
    current_cost: float = Field(..., ge=0)
    weight: float = Field(default=1.0, ge=0)


class InflationForecastRequest(BaseModel):
    items: List[InflationItem]
    cpi_rate: float = Field(default=7.0, ge=0)
    years: int = Field(..., ge=1, le=30)


class InflationProjection(BaseModel):
    name: str
    current_cost: float
    projected_cost: float
    increase_pct: float


class InflationForecastResponse(BaseModel):
    base_scenario: List[InflationProjection]
    optimistic_scenario: List[InflationProjection]
    pessimistic_scenario: List[InflationProjection]
    total_current: float
    total_projected: float
    meta: Dict[str, str]


class DashboardSummary(BaseModel):
    total_income: float
    total_expenses: float
    surplus: float
    dti: float
    safe_to_spend: float
    fun_budget: float
    goal_progress_pct: float
    debt_payoff_eta_months: Optional[int]


# ============ AI ============
class AIChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)


class AIChatResponse(BaseModel):
    response: str
    intent: str
    blocked: bool = False
    meta: Dict[str, str]


class AIInsight(BaseModel):
    type: str
    title: str
    message: str
    severity: str  # info, warning, critical


class AIInsightsResponse(BaseModel):
    insights: List[AIInsight]


class AIRulesUpdate(BaseModel):
    fun_ratio: Optional[float] = Field(None, ge=0, le=1)
    category_caps: Optional[Dict[str, float]] = None
    velocity_threshold_k: Optional[float] = Field(None, ge=0)
    merchant_rules: Optional[List[Dict[str, Any]]] = None


class ConsentUpdate(BaseModel):
    scope: ConsentScope
    granted: bool


# ============ IMPORTS ============
class ImportSummary(BaseModel):
    filename: str
    processed_count: int
    category_totals: Dict[str, float]
    created_at: datetime
"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
from datetime import datetime
import re


# ============= Auth Schemas =============
class UserRegister(BaseModel):
    """User registration schema."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Enforce password strength:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    """User login schema."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    """User profile response."""
    id: int
    email: str
    locale: str
    currency: str
    risk_tolerance: Optional[str] = None
    monthly_net_income: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """User profile update schema."""
    locale: Optional[str] = None
    currency: Optional[str] = None
    risk_tolerance: Optional[str] = None
    monthly_net_income: Optional[float] = None


# ============= Expense Schemas =============
class ExpenseCreate(BaseModel):
    """Create expense schema."""
    name: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(..., gt=0)
    type: str = Field(..., pattern="^(fixed|variable)$")


class ExpenseResponse(BaseModel):
    """Expense response schema."""
    id: int
    user_id: int
    name: str
    amount: float
    type: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Debt Schemas =============
class DebtCreate(BaseModel):
    """Create debt account schema."""
    name: str = Field(..., min_length=1, max_length=255)
    principal: float = Field(..., gt=0)
    annual_rate_pct: float = Field(..., ge=0)
    term_months: int = Field(..., ge=1)
    current_emi: float = Field(..., ge=0)


class DebtResponse(BaseModel):
    """Debt account response schema."""
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


# ============= Goal Schemas =============
class GoalCreate(BaseModel):
    """Create goal schema."""
    name: str = Field(..., min_length=1, max_length=255)
    target_amount: float = Field(..., gt=0)
    saved_amount: float = Field(default=0.0, ge=0)
    target_date: Optional[datetime] = None
    priority: int = Field(default=1, ge=1)


class GoalResponse(BaseModel):
    """Goal response schema."""
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


# ============= Calculation Schemas =============
class LoanPreAssessmentRequest(BaseModel):
    """Loan pre-assessment request."""
    income: float = Field(..., gt=0)
    existing_monthly_debt: float = Field(..., ge=0)
    annual_rate_pct: float = Field(..., gt=0)
    term_months: int = Field(..., ge=1)


class StressTestResult(BaseModel):
    """Stress test scenario result."""
    scenario: str
    new_emi: float
    dti: float
    is_affordable: bool


class LoanPreAssessmentResponse(BaseModel):
    """Loan pre-assessment response."""
    dti: float
    affordable_emi: float
    estimated_principal: float
    stress_tests: List[StressTestResult]
    meta: dict


class LoanPayoffPlanRequest(BaseModel):
    """Loan payoff plan request."""
    principal: float = Field(..., gt=0)
    annual_rate_pct: float = Field(..., gt=0)
    term_months: int = Field(..., ge=1)
    extra_payment: float = Field(default=0.0, ge=0)


class LoanPayoffPlanResponse(BaseModel):
    """Loan payoff plan response."""
    monthly_emi: float
    total_interest: float
    total_paid: float
    months_saved: int
    interest_saved: float
    meta: dict


class InflationProjection(BaseModel):
    """Single year inflation projection."""
    year: int
    estimated_price: float


class InflationForecastRequest(BaseModel):
    """Inflation forecast request."""
    current_price: float = Field(..., gt=0)
    annual_cpi_rate: float = Field(..., ge=0)
    years: int = Field(..., ge=1, le=30)


class InflationForecastResponse(BaseModel):
    """Inflation forecast response."""
    projections: List[InflationProjection]
    meta: dict


class DashboardSummary(BaseModel):
    """Dashboard summary response."""
    total_income: float
    total_fixed_expenses: float
    total_variable_expenses: float
    total_debt_emi: float
    total_savings_needed: float
    remaining_balance: float
    dti: float
    safe_to_spend: float
    fun_budget: float


# ============= AI Schemas =============
class AIInsight(BaseModel):
    """AI insight response."""
    answer: str
    intent: str
    is_blocked: bool
    meta: dict


class AIAskRequest(BaseModel):
    """AI ask request."""
    question: str = Field(..., min_length=1, max_length=1000)


# ============= Import Schemas =============
class CSVUploadResponse(BaseModel):
    """CSV upload response."""
    filename: str
    rows_processed: int
    expenses_added: int
    message: str


class ExportResponse(BaseModel):
    """Export data response."""
    expenses: List[ExpenseResponse]
    debts: List[DebtResponse]
    goals: List[GoalResponse]
"""Calculation endpoints for financial computations."""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User, Expense, DebtAccount, Goal
from app.schemas import (
    LoanPreAssessmentRequest, LoanPreAssessmentResponse,
    LoanPayoffPlanRequest, LoanPayoffPlanResponse,
    InflationForecastRequest, InflationForecastResponse,
    InflationProjection, StressTestResult, DashboardSummary
)
from app.security import get_current_user
from app.services import calculators
from app.services.compliance import get_loan_meta, get_projection_meta, get_calc_meta
from app.settings import settings

router = APIRouter(prefix="/calc", tags=["calculations"])


@router.post("/loan-pre-assessment", response_model=LoanPreAssessmentResponse)
def loan_pre_assessment(
    request: LoanPreAssessmentRequest,
    user: User = Depends(get_current_user)
):
    """
    Estimate loan affordability (educational only).
    
    Returns DTI, affordable EMI cap, estimated principal, and stress test scenarios.
    """
    # Base DTI
    dti = calculators.dti(request.existing_monthly_debt, request.income)
    
    # Affordable EMI cap (40% of income - existing debt)
    max_total_debt = request.income * settings.MAX_DTI_RATIO
    affordable_new_emi = max_total_debt - request.existing_monthly_debt
    affordable_new_emi = max(0, affordable_new_emi)
    
    # Estimated principal
    principal_est = calculators.principal_from_emi(
        affordable_new_emi,
        request.annual_rate_pct,
        request.term_months
    )
    
    # Stress tests
    stress_tests = []
    
    # Scenario 1: +2% interest rate
    stress_rate = request.annual_rate_pct + 2
    stress_emi_1 = calculators.emi(principal_est, stress_rate, request.term_months)
    stress_dti_1 = calculators.dti(
        request.existing_monthly_debt + stress_emi_1,
        request.income
    )
    stress_tests.append(StressTestResult(
        scenario="Interest rate +2%",
        dti=round(stress_dti_1, 4),
        affordable_emi=round(affordable_new_emi, 2),
        principal_est=round(principal_est, 2)
    ))
    
    # Scenario 2: -10% income
    stress_income = request.income * 0.9
    stress_affordable_2 = (stress_income * settings.MAX_DTI_RATIO) - request.existing_monthly_debt
    stress_affordable_2 = max(0, stress_affordable_2)
    stress_principal_2 = calculators.principal_from_emi(
        stress_affordable_2,
        request.annual_rate_pct,
        request.term_months
    )
    stress_dti_2 = calculators.dti(
        request.existing_monthly_debt,
        stress_income
    )
    stress_tests.append(StressTestResult(
        scenario="Income -10%",
        dti=round(stress_dti_2, 4),
        affordable_emi=round(stress_affordable_2, 2),
        principal_est=round(stress_principal_2, 2)
    ))
    
    return LoanPreAssessmentResponse(
        dti=round(dti, 4),
        affordable_emi_cap=round(affordable_new_emi, 2),
        principal_est=round(principal_est, 2),
        stress_tests=stress_tests,
        meta=get_loan_meta()
    )


@router.post("/loan-payoff-plan", response_model=LoanPayoffPlanResponse)
def loan_payoff_plan(
    request: LoanPayoffPlanRequest,
    user: User = Depends(get_current_user)
):
    """
    Calculate payoff plan for existing loan.
    
    Returns required EMI, total interest, and total payment.
    """
    required_emi = calculators.required_emi_to_finish(
        request.principal,
        request.annual_rate_pct,
        request.months_remaining
    )
    
    total_payment = required_emi * request.months_remaining
    total_interest = total_payment - request.principal
    
    return LoanPayoffPlanResponse(
        required_emi=round(required_emi, 2),
        total_interest=round(total_interest, 2),
        total_payment=round(total_payment, 2),
        meta=get_calc_meta()
    )


@router.post("/inflation-forecast", response_model=InflationForecastResponse)
def inflation_forecast(
    request: InflationForecastRequest,
    user: User = Depends(get_current_user)
):
    """
    Project inflation impact on essential expenses.
    
    Returns base, optimistic, and pessimistic scenarios.
    """
    base_projections = []
    optimistic_projections = []
    pessimistic_projections = []
    
    total_current = sum(item.current_cost * item.weight for item in request.items)
    total_projected = 0.0
    
    for item in request.items:
        # Base scenario
        base_future = calculators.inflation_projection(
            item.current_cost,
            request.cpi_rate,
            request.years
        )
        base_increase = ((base_future - item.current_cost) / item.current_cost) * 100 if item.current_cost > 0 else 0
        base_projections.append(InflationProjection(
            name=item.name,
            current_cost=round(item.current_cost, 2),
            projected_cost=round(base_future, 2),
            increase_pct=round(base_increase, 2)
        ))
        total_projected += base_future * item.weight
        
        # Optimistic scenario (-2% from base)
        opt_future = calculators.inflation_projection(
            item.current_cost,
            max(0, request.cpi_rate - 2),
            request.years
        )
        opt_increase = ((opt_future - item.current_cost) / item.current_cost) * 100 if item.current_cost > 0 else 0
        optimistic_projections.append(InflationProjection(
            name=item.name,
            current_cost=round(item.current_cost, 2),
            projected_cost=round(opt_future, 2),
            increase_pct=round(opt_increase, 2)
        ))
        
        # Pessimistic scenario (+3% from base)
        pess_future = calculators.inflation_projection(
            item.current_cost,
            request.cpi_rate + 3,
            request.years
        )
        pess_increase = ((pess_future - item.current_cost) / item.current_cost) * 100 if item.current_cost > 0 else 0
        pessimistic_projections.append(InflationProjection(
            name=item.name,
            current_cost=round(item.current_cost, 2),
            projected_cost=round(pess_future, 2),
            increase_pct=round(pess_increase, 2)
        ))
    
    return InflationForecastResponse(
        base_scenario=base_projections,
        optimistic_scenario=optimistic_projections,
        pessimistic_scenario=pessimistic_projections,
        total_current=round(total_current, 2),
        total_projected=round(total_projected, 2),
        meta=get_projection_meta()
    )


@router.get("/dashboard", response_model=DashboardSummary)
def get_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Get dashboard summary with key financial metrics.
    """
    # Fetch user data
    expenses = db.query(Expense).filter(Expense.user_id == user.id).all()
    debts = db.query(DebtAccount).filter(DebtAccount.user_id == user.id).all()
    goals = db.query(Goal).filter(Goal.user_id == user.id).all()
    
    # Calculate totals
    total_expenses = sum(e.amount for e in expenses)
    total_debt_emi = sum(d.current_emi for d in debts)
    total_income = user.monthly_net_income
    surplus = total_income - total_expenses - total_debt_emi
    
    # DTI
    dti_ratio = calculators.dti(total_debt_emi, total_income)
    
    # Safe to spend (simplified: surplus minus 20% for goals)
    goal_allocation = surplus * 0.2 if surplus > 0 else 0
    safe_spend = max(0, surplus - goal_allocation)
    
    # Fun budget
    fun_budget_amt = calculators.fun_budget(total_income, settings.DEFAULT_FUN_RATIO)
    
    # Goal progress
    total_goal_target = sum(g.target_amount for g in goals)
    total_goal_saved = sum(g.saved_amount for g in goals)
    goal_progress = (total_goal_saved / total_goal_target * 100) if total_goal_target > 0 else 0
    
    # Debt payoff ETA (simplified: total remaining / total EMI)
    total_principal_remaining = sum(d.principal for d in debts)
    debt_eta = int(total_principal_remaining / total_debt_emi) if total_debt_emi > 0 else None
    
    return DashboardSummary(
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        surplus=round(surplus, 2),
        dti=round(dti_ratio, 4),
        safe_to_spend=round(safe_spend, 2),
        fun_budget=round(fun_budget_amt, 2),
        goal_progress_pct=round(goal_progress, 2),
        debt_payoff_eta_months=debt_eta
    )
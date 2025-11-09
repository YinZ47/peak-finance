"""User profile management routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User, Expense, DebtAccount, Goal
from app.schemas import (
    UserProfile, UserProfileUpdate,
    ExpenseCreate, ExpenseResponse,
    DebtCreate, DebtResponse,
    GoalCreate, GoalResponse
)
from app.security import get_current_user
from app.services.audit import log_action

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=UserProfile)
def get_profile(user: User = Depends(get_current_user)):
    """Get user profile."""
    return user


@router.post("", response_model=UserProfile)
def update_profile(
    updates: UserProfileUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update user profile."""
    update_data = updates.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    log_action(db, "profile_updated", user, update_data)
    
    return user


# ============= EXPENSES =============

@router.get("/expenses", response_model=List[ExpenseResponse])
def list_expenses(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List all user expenses."""
    return db.query(Expense).filter(Expense.user_id == user.id).all()


@router.post("/expenses", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Create a new expense."""
    new_expense = Expense(
        user_id=user.id,
        name=expense.name,
        amount=expense.amount,
        type=expense.type
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    
    log_action(db, "expense_created", user, {"name": expense.name, "amount": expense.amount})
    
    return new_expense


@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Delete an expense."""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == user.id
    ).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    db.delete(expense)
    db.commit()
    
    log_action(db, "expense_deleted", user, {"id": expense_id})
    
    return None


# ============= DEBTS =============

@router.get("/debts", response_model=List[DebtResponse])
def list_debts(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List all user debts."""
    return db.query(DebtAccount).filter(DebtAccount.user_id == user.id).all()


@router.post("/debts", response_model=DebtResponse, status_code=status.HTTP_201_CREATED)
def create_debt(
    debt: DebtCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Create a new debt account."""
    new_debt = DebtAccount(
        user_id=user.id,
        name=debt.name,
        principal=debt.principal,
        annual_rate_pct=debt.annual_rate_pct,
        term_months=debt.term_months,
        current_emi=debt.current_emi
    )
    db.add(new_debt)
    db.commit()
    db.refresh(new_debt)
    
    log_action(db, "debt_created", user, {"name": debt.name, "principal": debt.principal})
    
    return new_debt


@router.delete("/debts/{debt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_debt(
    debt_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Delete a debt account."""
    debt = db.query(DebtAccount).filter(
        DebtAccount.id == debt_id,
        DebtAccount.user_id == user.id
    ).first()
    
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    
    db.delete(debt)
    db.commit()
    
    log_action(db, "debt_deleted", user, {"id": debt_id})
    
    return None


# ============= GOALS =============

@router.get("/goals", response_model=List[GoalResponse])
def list_goals(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List all user goals."""
    return db.query(Goal).filter(Goal.user_id == user.id).order_by(Goal.priority.desc()).all()


@router.post("/goals", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    goal: GoalCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Create a new financial goal."""
    new_goal = Goal(
        user_id=user.id,
        name=goal.name,
        target_amount=goal.target_amount,
        saved_amount=goal.saved_amount,
        priority=goal.priority
    )
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    
    log_action(db, "goal_created", user, {"name": goal.name, "target": goal.target_amount})
    
    return new_goal


@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Delete a financial goal."""
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    db.delete(goal)
    db.commit()
    
    log_action(db, "goal_deleted", user, {"id": goal_id})
    
    return None
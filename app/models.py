"""SQLAlchemy database models."""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, 
    ForeignKey, Enum, Text, CheckConstraint
)
from sqlalchemy.orm import relationship
from app.db import Base


class RiskTolerance(str, PyEnum):
    """User risk tolerance levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ExpenseType(str, PyEnum):
    """Expense categorization."""
    FIXED = "fixed"
    VARIABLE = "variable"


class ConsentScope(str, PyEnum):
    """Types of user consent."""
    READ_STATEMENTS = "read_statements"
    SHARE_WITH_PARTNER = "share_with_partner"
    AI_TRAINING_OPT_IN = "ai_training_opt_in"


class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    locale = Column(String(10), default="bn_BD")
    currency = Column(String(3), default="BDT")
    risk_tolerance = Column(Enum(RiskTolerance), nullable=True)
    monthly_net_income = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")
    debts = relationship("DebtAccount", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    consents = relationship("Consent", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    imports = relationship("TransactionImport", back_populates="user", cascade="all, delete-orphan")
    ai_rules = relationship("AIRule", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Expense(Base):
    """User expense model."""
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(Enum(ExpenseType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="expenses")
    
    __table_args__ = (
        CheckConstraint('amount >= 0', name='check_expense_amount_positive'),
    )


class DebtAccount(Base):
    """User debt/loan account model."""
    __tablename__ = "debt_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    principal = Column(Float, nullable=False)
    annual_rate_pct = Column(Float, nullable=False)
    term_months = Column(Integer, nullable=False)
    current_emi = Column(Float, nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="debts")
    
    __table_args__ = (
        CheckConstraint('principal >= 0', name='check_principal_positive'),
        CheckConstraint('annual_rate_pct >= 0', name='check_rate_positive'),
        CheckConstraint('term_months >= 1', name='check_term_positive'),
        CheckConstraint('current_emi >= 0', name='check_emi_positive'),
    )


class Goal(Base):
    """User financial goal model."""
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    target_amount = Column(Float, nullable=False)
    saved_amount = Column(Float, default=0.0)
    target_date = Column(DateTime, nullable=True)
    priority = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="goals")
    
    __table_args__ = (
        CheckConstraint('target_amount >= 0', name='check_target_positive'),
        CheckConstraint('saved_amount >= 0', name='check_saved_positive'),
    )


class Consent(Base):
    """User consent tracking."""
    __tablename__ = "consents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scope = Column(Enum(ConsentScope), nullable=False)
    granted = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="consents")


class AuditLog(Base):
    """Audit log for sensitive operations."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(255), nullable=False)
    payload_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="audit_logs")


class FeatureFlags(Base):
    """Global feature flags (singleton)."""
    __tablename__ = "feature_flags"
    
    id = Column(Integer, primary_key=True, default=1)
    IS_REGULATED_PARTNER = Column(Boolean, default=False)


class TransactionImport(Base):
    """CSV import tracking."""
    __tablename__ = "transaction_imports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    csv_filename = Column(String(255), nullable=False)
    processed_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="imports")


class AIRule(Base):
    """AI advisor user-specific rules."""
    __tablename__ = "ai_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    fun_ratio = Column(Float, default=0.15)  # 15% default
    category_caps_json = Column(Text, default="{}")  # JSON dict of category: cap
    velocity_threshold_k = Column(Float, default=2.0)  # Sigma multiplier for anomaly detection
    merchant_rules_json = Column(Text, default="[]")  # JSON list of merchant rules
    
    user = relationship("User", back_populates="ai_rules")
    
    __table_args__ = (
        CheckConstraint('fun_ratio >= 0 AND fun_ratio <= 1', name='check_fun_ratio_range'),
    )
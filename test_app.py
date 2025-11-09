"""Quick test script to verify application functionality."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Peak Finance - Application Test")
print("=" * 60)

# Test 1: Import all modules
print("\n✅ Test 1: Importing all modules...")
try:
    from app import models, schemas, security, settings, db
    from app.routers import auth, profile, data, calc
    from app.services import ai, audit, calculators, compliance, imports as import_service
    print("   ✅ All modules imported successfully")
except ImportError as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# Test 2: Database initialization
print("\n✅ Test 2: Database initialization...")
try:
    from app.db import init_db
    init_db()
    print("   ✅ Database initialized successfully")
except Exception as e:
    print(f"   ❌ Database error: {e}")
    sys.exit(1)

# Test 3: Settings validation
print("\n✅ Test 3: Settings validation...")
try:
    from app.settings import settings
    assert len(settings.SECRET_KEY) >= 32, "SECRET_KEY too short"
    assert settings.DATABASE_URL, "DATABASE_URL not set"
    print(f"   ✅ Settings loaded: {settings.DATABASE_URL}")
except Exception as e:
    print(f"   ❌ Settings error: {e}")
    sys.exit(1)

# Test 4: Calculator functions
print("\n✅ Test 4: Calculator functions...")
try:
    from app.services.calculators import emi, dti, fun_budget, inflation_projection
    
    # Test EMI calculation
    test_emi = emi(100000, 10.0, 12)
    assert test_emi > 0, "EMI calculation failed"
    
    # Test DTI calculation
    test_dti = dti(10000, 50000)
    assert 0 <= test_dti <= 1, "DTI calculation failed"
    
    # Test fun budget
    test_fun = fun_budget(50000, 0.15)
    assert test_fun >= 0, "Fun budget calculation failed"
    
    # Test inflation projection
    test_inflation = inflation_projection(1000, 7.0, 5)
    assert test_inflation > 1000, "Inflation projection failed"
    
    print(f"   ✅ EMI(100k, 10%, 12m) = {test_emi:.2f}")
    print(f"   ✅ DTI(10k debt, 50k income) = {test_dti:.2%}")
    print(f"   ✅ Fun budget (50k, 15%) = {test_fun:.2f}")
    print(f"   ✅ Inflation projection = {test_inflation:.2f}")
except Exception as e:
    print(f"   ❌ Calculator error: {e}")
    sys.exit(1)

# Test 5: Security functions
print("\n✅ Test 5: Security functions...")
try:
    from app.security import hash_password, verify_password, create_access_token
    
    test_password = "TestPassword123"
    hashed = hash_password(test_password)
    assert verify_password(test_password, hashed), "Password verification failed"
    
    token = create_access_token(data={"sub": 1})
    assert token and len(token) > 20, "Token generation failed"
    
    print(f"   ✅ Password hashing works")
    print(f"   ✅ Password verification works")
    print(f"   ✅ JWT token generation works")
except Exception as e:
    print(f"   ❌ Security error: {e}")
    sys.exit(1)

# Test 6: Schema validation
print("\n✅ Test 6: Schema validation...")
try:
    from app.schemas import UserRegister, LoanPreAssessmentRequest
    
    # Valid user registration
    user = UserRegister(email="test@example.com", password="TestPass123")
    assert user.email == "test@example.com", "Email validation failed"
    
    # Valid loan request
    loan_req = LoanPreAssessmentRequest(
        income=50000,
        existing_monthly_debt=10000,
        annual_rate_pct=10.0,
        term_months=12
    )
    assert loan_req.income == 50000, "Loan request validation failed"
    
    print(f"   ✅ UserRegister schema works")
    print(f"   ✅ LoanPreAssessmentRequest schema works")
except Exception as e:
    print(f"   ❌ Schema error: {e}")
    sys.exit(1)

# Test 7: AI service
print("\n✅ Test 7: AI service...")
try:
    from app.services.ai import AIProvider, IntentCategory
    
    ai_provider = AIProvider()
    print(f"   ✅ AI Provider initialized (configured: {ai_provider.is_configured})")
    
    # Test mock response
    response = ai_provider._mock_response("budget help", "income: 50000")
    assert len(response) > 0, "Mock response generation failed"
    print(f"   ✅ Mock AI response works")
except Exception as e:
    print(f"   ❌ AI service error: {e}")
    sys.exit(1)

# Final summary
print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\nYour application is ready to run:")
print("  python -m uvicorn main:app --host 0.0.0.0 --port 8000")
print("\nOr with auto-reload for development:")
print("  python -m uvicorn main:app --reload")
print("\nAccess the application at:")
print("  http://localhost:8000")
print("\nAPI Documentation:")
print("  http://localhost:8000/api/docs")
print("=" * 60)

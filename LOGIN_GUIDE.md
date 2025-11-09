# 🔐 Peak Finance - Login Guide

## 🚀 Quick Start: How to Log In

### Step 1: Start the Application

The server is already running at: **http://127.0.0.1:8000**

If you need to start it manually:
```powershell
python -m uvicorn main:app --reload
```

---

### Step 2: Access the Application

Open your web browser and go to:
```
http://localhost:8000
```

or

```
http://127.0.0.1:8000
```

---

### Step 3: Create an Account (First Time)

Since this is a fresh installation, you need to **register first**:

1. **Click "Get Started Free"** on the landing page, or
2. **Navigate to:** http://localhost:8000/auth
3. You'll see the authentication page with two tabs: **Login** and **Register**

#### To Register:
1. Click the **"Register"** tab
2. Enter your email (e.g., `user@example.com`)
3. Enter a strong password that includes:
   - ✅ At least 8 characters
   - ✅ At least one uppercase letter (A-Z)
   - ✅ At least one lowercase letter (a-z)
   - ✅ At least one digit (0-9)
   
   **Example valid password:** `TestPass123`

4. Click **"Create Account"**
5. You'll be automatically logged in and redirected to the dashboard

---

### Step 4: Log In (Returning Users)

Once you have an account:

1. Go to: http://localhost:8000/auth
2. Make sure you're on the **"Login"** tab
3. Enter your email
4. Enter your password
5. Click **"Sign In"**
6. You'll be redirected to the dashboard at http://localhost:8000/dashboard

---

## 🧪 Test Account (Quick Testing)

Want to test quickly? Here's how to create a test account:

### Option 1: Via Web Interface
1. Go to http://localhost:8000/auth
2. Click **Register** tab
3. Use these credentials:
   - **Email:** `test@example.com`
   - **Password:** `TestPass123`
4. Click **"Create Account"**

### Option 2: Via API (using PowerShell)

**Register a test user:**
```powershell
$body = @{
    email = "test@example.com"
    password = "TestPass123"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/auth/register" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

**Then log in:**
```powershell
$body = @{
    email = "test@example.com"
    password = "TestPass123"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body `
    -SessionVariable session
```

---

## 🔍 How Authentication Works

### Security Features:
1. **Password Hashing:** Your password is never stored in plain text (uses bcrypt)
2. **JWT Tokens:** Secure token-based authentication
3. **HTTP-Only Cookies:** Tokens stored securely in cookies (CSRF protection)
4. **Session Management:** Automatic token validation on protected pages

### Login Flow:
```
User enters credentials
    ↓
Backend validates password (bcrypt)
    ↓
Generates JWT token (expires in 1 day)
    ↓
Sets HTTP-only cookie
    ↓
Returns token + redirects to dashboard
    ↓
All API requests include token automatically
```

---

## 📱 What You Can Do After Login

Once logged in, you have access to:

### 1. **Dashboard** (http://localhost:8000/dashboard)
- View financial summary
- Quick access to all features

### 2. **Profile Management**
- Update your profile
- Set risk tolerance
- Configure monthly income

### 3. **Expense Tracking**
- Add fixed expenses (rent, utilities)
- Add variable expenses (groceries, entertainment)
- View expense breakdown

### 4. **Debt Management**
- Track loans and debts
- Calculate EMI payments
- Monitor debt-to-income ratio

### 5. **Financial Goals**
- Set savings goals
- Track progress
- Prioritize goals

### 6. **AI Financial Advisor**
- Ask financial questions
- Get personalized recommendations
- Educational guidance

### 7. **Calculators**
- Loan affordability checker
- EMI calculator
- Inflation forecaster
- Debt payoff planner

### 8. **Data Management**
- Import transactions via CSV
- Export all your data
- Backup your information

---

## 🐛 Troubleshooting

### Problem: "Incorrect email or password"
**Solution:**
- Make sure you registered first
- Check your email spelling
- Verify password (case-sensitive)
- Try the "Remember me" checkbox

### Problem: Can't access dashboard (redirected to login)
**Solution:**
- Your session may have expired (tokens last 1 day)
- Clear browser cookies and log in again
- Make sure cookies are enabled in your browser

### Problem: Page not loading
**Solution:**
- Verify server is running (check terminal for errors)
- Try http://localhost:8000 instead of http://127.0.0.1:8000
- Clear browser cache (Ctrl+F5)

### Problem: Registration fails
**Solution:**
- Email must be valid format (e.g., user@example.com)
- Password must meet requirements (8+ chars, uppercase, lowercase, digit)
- Email cannot be already registered (use different email)

---

## 🔐 Password Requirements

Your password MUST include:
- ✅ Minimum 8 characters
- ✅ At least one uppercase letter (A-Z)
- ✅ At least one lowercase letter (a-z)
- ✅ At least one digit (0-9)

**Valid Examples:**
- `TestPass123`
- `MySecret2024`
- `Finance$123`

**Invalid Examples:**
- `password` ❌ (no uppercase, no digit)
- `PASSWORD123` ❌ (no lowercase)
- `TestPass` ❌ (no digit)
- `Test123` ❌ (less than 8 characters)

---

## 📊 API Endpoints (for developers)

### Register
```
POST http://localhost:8000/api/auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "YourPass123"
}
```

### Login
```
POST http://localhost:8000/api/auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "YourPass123"
}
```

### Get Current User
```
GET http://localhost:8000/api/auth/me
Cookie: access_token=<your-token>
```

### Logout
```
POST http://localhost:8000/api/auth/logout
Cookie: access_token=<your-token>
```

---

## 🎯 Quick Access URLs

- **Landing Page:** http://localhost:8000
- **Login/Register:** http://localhost:8000/auth
- **Dashboard:** http://localhost:8000/dashboard
- **API Docs:** http://localhost:8000/api/docs
- **Health Check:** http://localhost:8000/health

---

## 💡 Tips

1. **Use Strong Passwords:** Even for testing, practice good security habits
2. **Remember Me:** Check this box to stay logged in longer
3. **Logout When Done:** Click "Logout" in the navigation to clear session
4. **Test API Docs:** Visit /api/docs to test API endpoints interactively
5. **Multiple Accounts:** You can create multiple test accounts with different emails

---

## 🆘 Need Help?

### Check Server Status
```powershell
# Visit health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","version":"1.0.0"}
```

### View Server Logs
Look at the terminal where you ran `uvicorn` - all requests are logged there.

### Check Database
```powershell
# Verify database exists
dir app.db

# Reinitialize if needed
python -c "from app.db import init_db; init_db()"
```

### Interactive API Testing
1. Go to http://localhost:8000/api/docs
2. Click "Try it out" on any endpoint
3. Enter parameters and execute
4. See the response in real-time

---

## 📝 Example Login Session

Here's what a typical first-time user experience looks like:

1. **Open:** http://localhost:8000
2. **Click:** "Get Started Free" button
3. **On auth page:**
   - Email: `demo@example.com`
   - Password: `DemoPass123`
   - Click "Create Account"
4. **Automatic redirect** to dashboard
5. **Start using** the app:
   - Add your monthly income
   - Add some expenses
   - Set financial goals
   - Try the calculators
6. **When done:** Click "Logout" in top navigation

---

**Server Status:** 🟢 Running on http://127.0.0.1:8000

**Ready to start?** Open http://localhost:8000 in your browser now!

---

*Last Updated: November 10, 2025*

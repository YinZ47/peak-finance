# Peak Finance 💰

**Personal Finance Web App for Bangladesh (Educational)**

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Virtual environment (recommended)

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd peak-finance
```

2. **Create virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
copy .env.example .env
# Edit .env and update SECRET_KEY with a secure random string
```

5. **Initialize database:**
```bash
python -c "from app.db import init_db; init_db(); print('Database initialized')"
```

6. **Run the server:**
```bash
python -m uvicorn main:app --reload
```

7. **Access the application:**
- Main app: http://localhost:8000
- API docs: http://localhost:8000/api/docs

## 📋 Features

### Core Features
- **User Authentication** - JWT-based secure login/register
- **Dashboard** - Real-time financial overview with key metrics
- **Expense Tracking** - Add, view, and delete expenses
- **Debt Management** - Track debts with EMI calculations
- **Goal Planning** - Set and monitor savings goals
- **Financial Calculators**:
  - Loan Pre-Assessment
  - DTI Calculator
  - Inflation Forecasting
  - EMI Calculator

### Technical Features
- RESTful API with FastAPI
- SQLAlchemy ORM with SQLite (PostgreSQL for production)
- Pydantic validation
- JWT authentication with bcrypt
- Responsive UI with vanilla JavaScript
- OpenAPI documentation

## 🏗️ Project Structure

```
peak-finance/
├── app/
│   ├── routers/          # API endpoints
│   │   ├── auth.py       # Authentication
│   │   ├── profile.py    # User profile & data CRUD
│   │   ├── calc.py       # Financial calculations
│   │   └── data.py       # Data import/export
│   ├── services/         # Business logic
│   │   ├── calculators.py # Financial formulas
│   │   ├── compliance.py  # Regulatory metadata
│   │   ├── audit.py       # Audit logging
│   │   ├── ai.py          # AI advisor (optional)
│   │   └── imports.py     # CSV parsing
│   ├── templates/        # Jinja2 HTML templates
│   ├── static/           # CSS, JS, images
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   ├── security.py       # JWT & auth utilities
│   ├── settings.py       # Configuration
│   └── db.py             # Database setup
├── main.py               # FastAPI application
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Multi-container setup
└── README.md             # This file
```

## 🔒 Security

- **JWT Authentication**: Secure token-based auth with 1-day expiration
- **Password Hashing**: Bcrypt with salt
- **Input Validation**: Pydantic schemas on all endpoints
- **CORS**: Configurable origins
- **SQL Injection Protection**: SQLAlchemy ORM parameterization

## 📊 API Endpoints

### Authentication (`/api/auth`)
- `POST /api/auth/register` - Create new user
- `POST /api/auth/login` - Login and get JWT token

### Profile (`/api/profile`)
- `GET /api/profile/me` - Get current user profile
- `PUT /api/profile/me` - Update user profile
- `GET /api/profile/expenses` - List user expenses
- `POST /api/profile/expenses` - Add expense
- `DELETE /api/profile/expenses/{id}` - Delete expense
- `GET /api/profile/debts` - List user debts
- `POST /api/profile/debts` - Add debt
- `DELETE /api/profile/debts/{id}` - Delete debt
- `GET /api/profile/goals` - List user goals
- `POST /api/profile/goals` - Add goal
- `DELETE /api/profile/goals/{id}` - Delete goal

### Calculations (`/api/calc`)
- `POST /api/calc/loan-pre-assessment` - Loan affordability check
- `POST /api/calc/inflation-forecast` - Inflation projections
- `GET /api/calc/dashboard` - Dashboard summary metrics

## 🚢 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions covering:
- Docker deployment
- Traditional server setup
- Platform-as-a-Service (Heroku, Railway, etc.)
- Production best practices

## 📝 License

Educational project for demonstration purposes.

## 🤝 Contributing

This is an educational project. Feel free to fork and customize for your needs.
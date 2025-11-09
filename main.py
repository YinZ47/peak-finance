"""Main application entry point."""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path

from app.db import init_db
from app.settings import settings
from app.routers import auth, profile, data, calc

# Initialize FastAPI
app = FastAPI(
    title="Peak Finance",
    description="Personal Finance Web App for Bangladesh (Educational)",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers with /api prefix
app.include_router(auth.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(data.router, prefix="/api")
app.include_router(calc.router, prefix="/api")


@app.on_event("startup")
def on_startup():
    """Initialize database on startup."""
    init_db()


# Frontend routes
@app.get("/")
async def home(request: Request):
    """Landing page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dashboard")
async def dashboard(request: Request):
    """Dashboard page (requires auth)."""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/auth")
async def auth_page(request: Request):
    """Auth page (login/register)."""
    return templates.TemplateResponse("auth.html", {"request": request})


@app.get("/test-errors")
async def test_errors_page(request: Request):
    """Error handling test page."""
    return templates.TemplateResponse("test_errors.html", {"request": request})


@app.get("/favicon.ico")
async def favicon():
    """Serve the site favicon."""
    favicon_path = Path("app/static/favicon.ico")
    return FileResponse(favicon_path)


@app.get("/health")
def health():
    """Health check."""
    return {"status": "healthy", "version": "1.0.0"}
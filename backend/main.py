import hmac
import time
from collections import defaultdict
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import settings
from .database import Base, engine
from .routers import pantry, photos, recipes

Base.metadata.create_all(bind=engine)

# Disable interactive API docs in production
_docs_url = None if settings.environment == "production" else "/docs"
_redoc_url = None if settings.environment == "production" else "/redoc"

app = FastAPI(
    title="Amazon Groceries",
    version="0.1.0",
    docs_url=_docs_url,
    redoc_url=_redoc_url,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Api-Key"],
)


# --- API key authentication middleware ---
@app.middleware("http")
async def api_key_auth(request: Request, call_next):
    if not settings.api_key:
        return await call_next(request)
    path = request.url.path
    if not path.startswith("/api/") or path == "/api/health":
        return await call_next(request)
    provided_key = request.headers.get("X-Api-Key", "")
    if not hmac.compare_digest(provided_key, settings.api_key):
        return JSONResponse(status_code=401, content={"detail": "Invalid or missing API key"})
    return await call_next(request)


# --- Rate limiting middleware ---
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT = 30  # requests per window
_RATE_WINDOW = 60  # seconds
_MAX_TRACKED_IPS = 10000  # cap to prevent memory exhaustion


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    if not request.url.path.startswith("/api/"):
        return await call_next(request)
    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    _rate_limit_store[client_ip] = [
        t for t in _rate_limit_store[client_ip] if now - t < _RATE_WINDOW
    ]
    if len(_rate_limit_store) > _MAX_TRACKED_IPS:
        _rate_limit_store.clear()
    if len(_rate_limit_store[client_ip]) >= _RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please try again later."},
        )
    _rate_limit_store[client_ip].append(now)
    return await call_next(request)


BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# --- API Routers ---
app.include_router(pantry.router)
app.include_router(recipes.router)
app.include_router(photos.router)


# --- Web UI Routes ---
@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("pantry.html", {"request": request})


@app.get("/pantry")
def pantry_page(request: Request):
    return templates.TemplateResponse("pantry.html", {"request": request})


@app.get("/upload")
def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.get("/shopping")
def shopping_page(request: Request):
    return templates.TemplateResponse("shopping_list.html", {"request": request})


@app.get("/health")
def health():
    return {"status": "ok"}

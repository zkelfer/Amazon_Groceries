from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import Base, engine
from .routers import pantry, photos, recipes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Amazon Groceries", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

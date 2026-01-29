# Amazon Groceries — Context

## Status: All Phases Complete

## Components

### Backend (FastAPI) — `backend/`
- **Entry point**: `backend/main.py` — run with `uvicorn backend.main:app --reload`
- **Database**: SQLite via SQLAlchemy (`pantry.db`, auto-created)
- **API endpoints**:
  - `GET/POST /api/pantry` — list/create pantry items (supports `?search=` and `?category=`)
  - `POST /api/pantry/bulk` — bulk create
  - `GET/PUT/DELETE /api/pantry/{id}` — single item CRUD
  - `POST /api/recipes/diff` — compare ingredient list against pantry, returns in-pantry/missing status with Whole Foods URLs
  - `POST /api/recipes/parse` — parse raw ingredient strings into structured data
  - `POST /api/photos/upload` — photo upload (Claude Vision stubbed)
- **Web pages**: `/pantry`, `/upload`, `/shopping` — Jinja2-rendered UI
- **Services**:
  - `ingredient_parser.py` — wraps `ingredient-parser-nlp` (CRF model) for structured parsing
  - `ingredient_matcher.py` — fuzzy matching via `rapidfuzz` (token_set_ratio, threshold 70)
  - `shopping.py` — generates `amazon.com/s?k=TERM&i=wholefoods` URLs

### Chrome Extension — `extension/`
- **Manifest V3** with `activeTab` + `storage` permissions
- **Content scripts** injected on allrecipes, foodnetwork, NYT cooking, epicurious, bonappetit, seriouseats, simplyrecipes, delish, tasty
- **Extraction**: JSON-LD `schema.org/Recipe` first, DOM scraping fallback
- **Popup**: queries content script → sends to `/api/recipes/diff` → renders in-pantry/missing badges + Whole Foods links
- **API client**: fetch wrapper for `localhost:8000`

## Key Files
| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI app, CORS, router mounts, web UI routes |
| `backend/models.py` | SQLAlchemy ORM (PantryItem, ShoppingListItem) |
| `backend/schemas.py` | Pydantic request/response models |
| `backend/routers/pantry.py` | Pantry CRUD endpoints |
| `backend/routers/recipes.py` | Recipe diff + parse endpoints |
| `backend/routers/photos.py` | Photo upload stub |
| `backend/services/ingredient_parser.py` | ingredient-parser-nlp wrapper |
| `backend/services/ingredient_matcher.py` | rapidfuzz matching engine |
| `backend/services/shopping.py` | Whole Foods URL builder |
| `extension/manifest.json` | Chrome MV3 manifest |
| `extension/content.js` | Recipe page scraping |
| `extension/utils/recipe-extractors.js` | JSON-LD + DOM extraction |
| `extension/popup/popup.js` | Extension popup UI logic |

## Test Coverage
19 tests in `backend/tests/` — all passing:
- `test_pantry.py` — CRUD, bulk create, search, filtering, 404 handling
- `test_ingredient_parser.py` — structured parsing with/without quantities
- `test_ingredient_matcher.py` — exact match, fuzzy match, no match, edge cases
- `test_recipes.py` — recipe diff with pantry comparison, ingredient parsing

## Running
```bash
# Backend
cd Amazon_Groceries
source .venv/bin/activate
uvicorn backend.main:app --reload
# → http://localhost:8000 (web UI)
# → http://localhost:8000/docs (Swagger)

# Tests
python -m pytest backend/tests/ -v

# Extension
# Chrome → chrome://extensions → Developer mode → Load unpacked → select extension/
```

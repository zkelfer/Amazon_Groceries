from datetime import datetime

from pydantic import BaseModel


# --- Pantry ---


class PantryItemCreate(BaseModel):
    name: str
    quantity: float | None = None
    unit: str | None = None
    category: str | None = None
    notes: str | None = None


class PantryItemUpdate(BaseModel):
    name: str | None = None
    quantity: float | None = None
    unit: str | None = None
    category: str | None = None
    notes: str | None = None


class PantryItemOut(BaseModel):
    id: int
    name: str
    quantity: float | None
    unit: str | None
    category: str | None
    notes: str | None
    created_at: datetime | None
    updated_at: datetime | None

    model_config = {"from_attributes": True}


# --- Recipe diff ---


class RecipeDiffRequest(BaseModel):
    ingredients: list[str]
    recipe_url: str | None = None
    recipe_title: str | None = None


class IngredientStatus(BaseModel):
    raw: str
    name: str
    quantity: float | None = None
    unit: str | None = None
    in_pantry: bool = False
    pantry_match: str | None = None
    match_score: float = 0.0
    whole_foods_url: str | None = None


class RecipeDiffResponse(BaseModel):
    recipe_title: str | None
    recipe_url: str | None
    ingredients: list[IngredientStatus]
    missing_count: int
    in_pantry_count: int


# --- Parse ---


class ParseRequest(BaseModel):
    ingredients: list[str]


class ParsedIngredient(BaseModel):
    raw: str
    name: str
    quantity: float | None = None
    unit: str | None = None
    comment: str | None = None


class ParseResponse(BaseModel):
    parsed: list[ParsedIngredient]


# --- Photo upload ---


class PhotoUploadResponse(BaseModel):
    message: str
    items: list[PantryItemCreate]


# --- Shopping list ---


class ShoppingListItemOut(BaseModel):
    id: int
    name: str
    quantity: float | None
    unit: str | None
    source_recipe: str | None
    whole_foods_url: str | None
    purchased: bool
    created_at: datetime | None

    model_config = {"from_attributes": True}

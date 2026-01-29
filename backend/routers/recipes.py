from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import PantryItem
from ..schemas import (
    IngredientStatus,
    ParsedIngredient,
    ParseRequest,
    ParseResponse,
    RecipeDiffRequest,
    RecipeDiffResponse,
)
from ..services.ingredient_matcher import match_ingredient
from ..services.ingredient_parser import parse_single
from ..services.shopping import whole_foods_url

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


@router.post("/diff", response_model=RecipeDiffResponse)
def recipe_diff(body: RecipeDiffRequest, db: Session = Depends(get_db)):
    pantry_names = [item.name for item in db.query(PantryItem.name).all()]

    statuses: list[IngredientStatus] = []
    for raw in body.ingredients:
        parsed = parse_single(raw)
        match = match_ingredient(parsed.name, pantry_names)
        url = None if match.in_pantry else whole_foods_url(parsed.name)

        statuses.append(
            IngredientStatus(
                raw=raw,
                name=parsed.name,
                quantity=parsed.quantity,
                unit=parsed.unit,
                in_pantry=match.in_pantry,
                pantry_match=match.pantry_match,
                match_score=match.score,
                whole_foods_url=url,
            )
        )

    in_pantry_count = sum(1 for s in statuses if s.in_pantry)
    return RecipeDiffResponse(
        recipe_title=body.recipe_title,
        recipe_url=body.recipe_url,
        ingredients=statuses,
        missing_count=len(statuses) - in_pantry_count,
        in_pantry_count=in_pantry_count,
    )


@router.post("/parse", response_model=ParseResponse)
def parse_ingredients(body: ParseRequest):
    parsed = []
    for raw in body.ingredients:
        p = parse_single(raw)
        parsed.append(
            ParsedIngredient(
                raw=p.raw,
                name=p.name,
                quantity=p.quantity,
                unit=p.unit,
                comment=p.comment,
            )
        )
    return ParseResponse(parsed=parsed)

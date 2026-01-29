from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import PantryItem
from ..schemas import PantryItemCreate, PantryItemOut, PantryItemUpdate

router = APIRouter(prefix="/api/pantry", tags=["pantry"])


@router.get("", response_model=list[PantryItemOut])
def list_pantry(
    category: str | None = Query(None),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(PantryItem)
    if category:
        q = q.filter(func.lower(PantryItem.category) == category.lower())
    if search:
        q = q.filter(PantryItem.name.ilike(f"%{search}%"))
    return q.order_by(PantryItem.name).all()


@router.get("/{item_id}", response_model=PantryItemOut)
def get_pantry_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(PantryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("", response_model=PantryItemOut, status_code=201)
def create_pantry_item(body: PantryItemCreate, db: Session = Depends(get_db)):
    item = PantryItem(**body.model_dump())
    item.name = item.name.strip().lower()
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.post("/bulk", response_model=list[PantryItemOut], status_code=201)
def bulk_create_pantry_items(
    items: list[PantryItemCreate], db: Session = Depends(get_db)
):
    created = []
    for body in items:
        item = PantryItem(**body.model_dump())
        item.name = item.name.strip().lower()
        db.add(item)
        created.append(item)
    db.commit()
    for item in created:
        db.refresh(item)
    return created


@router.put("/{item_id}", response_model=PantryItemOut)
def update_pantry_item(
    item_id: int, body: PantryItemUpdate, db: Session = Depends(get_db)
):
    item = db.get(PantryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    updates = body.model_dump(exclude_unset=True)
    if "name" in updates and updates["name"]:
        updates["name"] = updates["name"].strip().lower()
    for key, value in updates.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_pantry_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(PantryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()

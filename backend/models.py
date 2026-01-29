from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Index, Integer, Text

from .database import Base


class PantryItem(Base):
    __tablename__ = "pantry_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, index=True)
    quantity = Column(Float, nullable=True)
    unit = Column(Text, nullable=True)
    category = Column(Text, nullable=True, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (Index("ix_pantry_name_lower", "name"),)


class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    quantity = Column(Float, nullable=True)
    unit = Column(Text, nullable=True)
    source_recipe = Column(Text, nullable=True)
    whole_foods_url = Column(Text, nullable=True)
    purchased = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

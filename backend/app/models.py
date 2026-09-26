import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from .database import Base


class Commodity(Base):
    __tablename__ = "commodities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=False)  # fresh_produce, dairy, meat, bakery, dry_snack, spice, ready_to_eat
    moisture_pct = Column(Float, nullable=False)
    fat_pct = Column(Float, nullable=False)
    ph = Column(Float, nullable=False)
    respiration_class = Column(String, nullable=False)  # none, low, medium, high
    oxygen_sensitive = Column(Boolean, default=False)
    light_sensitive = Column(Boolean, default=False)
    baseline_shelf_life_days = Column(Float, nullable=False)


class PackagingMaterial(Base):
    __tablename__ = "packaging_materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    otr_min = Column(Float, nullable=False)  # cc/m2/day
    otr_max = Column(Float, nullable=False)
    wvtr_min = Column(Float, nullable=False)  # g/m2/day
    wvtr_max = Column(Float, nullable=False)
    thickness_min_um = Column(Float, nullable=False)
    thickness_max_um = Column(Float, nullable=False)
    mechanical_strength = Column(String, nullable=False)  # low, medium, high
    sealability = Column(String, nullable=False)  # low, medium, high
    cost_tier = Column(Integer, nullable=False)  # 1 (cheapest) - 5 (most expensive)
    eco_score = Column(Integer, nullable=False)  # 1 - 10 (10 = most sustainable)
    recyclable = Column(Boolean, default=False)
    biodegradable = Column(Boolean, default=False)
    breathable = Column(Boolean, default=False)  # suitable for produce respiration / micro-perforation
    map_suitable = Column(Boolean, default=False)
    typical_uses = Column(Text, default="")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    passport_id = Column(String, unique=True, index=True, default=lambda: uuid.uuid4().hex[:10])
    commodity_name = Column(String, nullable=False)
    inputs_json = Column(Text, nullable=False)
    result_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

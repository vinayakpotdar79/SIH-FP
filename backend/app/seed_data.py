"""
Curated reference knowledge base.

Values are representative reference ranges compiled from public food-packaging
science literature (FAO post-harvest handling guides, published permeability
and produce-respiration-rate tables, general food packaging engineering
references) — see ../../DATA_SOURCES.md. They are meant for decision-support
demonstration purposes, not as certified lab measurements for a specific
product batch.
"""

from sqlalchemy.orm import Session

from .models import Commodity, PackagingMaterial

COMMODITIES = [
    # name, category, moisture_pct, fat_pct, ph, respiration_class, oxygen_sensitive, light_sensitive, baseline_shelf_life_days
    ("Mango", "fresh_produce", 82, 0.4, 4.0, "medium", True, False, 5),
    ("Tomato", "fresh_produce", 94, 0.2, 4.3, "medium", True, False, 7),
    ("Spinach / Leafy Greens", "fresh_produce", 91, 0.3, 6.5, "high", True, True, 3),
    ("Banana", "fresh_produce", 75, 0.3, 5.0, "high", True, False, 5),
    ("Strawberry / Berries", "fresh_produce", 91, 0.3, 3.5, "high", True, True, 3),
    ("Grapes", "fresh_produce", 81, 0.2, 3.5, "medium", True, False, 7),
    ("Potato", "fresh_produce", 79, 0.1, 5.8, "low", False, True, 60),
    ("Onion", "fresh_produce", 89, 0.1, 5.5, "low", False, False, 90),
    ("Milk (pasteurized)", "dairy", 87, 3.5, 6.7, "none", True, True, 7),
    ("Paneer / Soft Cheese", "dairy", 55, 25, 5.5, "none", True, False, 5),
    ("Butter", "dairy", 16, 80, 6.5, "none", True, True, 60),
    ("Chicken (fresh)", "meat", 75, 8, 6.0, "none", True, False, 2),
    ("Fish (fresh)", "meat", 78, 4, 6.5, "none", True, False, 1),
    ("Bread", "bakery", 38, 3, 5.5, "none", False, False, 4),
    ("Biscuits / Cookies", "bakery", 3, 20, 6.0, "none", True, False, 180),
    ("Namkeen / Fried Snacks", "dry_snack", 2, 30, 6.5, "none", True, False, 90),
    ("Potato Chips", "dry_snack", 1.5, 35, 6.2, "none", True, True, 120),
    ("Turmeric Powder", "spice", 8, 5, 6.0, "none", False, True, 365),
    ("Black Pepper (whole)", "spice", 10, 3, 6.0, "none", False, False, 730),
    ("Ready-to-Eat Curry (retort)", "ready_to_eat", 70, 10, 5.0, "none", True, False, 365),
]

MATERIALS = [
    # name, otr_min, otr_max, wvtr_min, wvtr_max, thick_min, thick_max, mech, seal, cost_tier,
    # eco_score, recyclable, biodegradable, breathable, map_suitable, typical_uses
    ("LDPE film", 7000, 8000, 6, 10, 25, 150, "medium", "high", 1, 4, True, False, False, True,
     "General produce/bread bags, liners"),
    ("HDPE film", 1500, 2000, 4, 8, 20, 100, "high", "medium", 1, 5, True, False, False, False,
     "Milk pouches, dry goods bags"),
    ("PP / BOPP film", 1500, 2500, 5, 10, 20, 40, "high", "medium", 2, 5, True, False, False, True,
     "Snack packets, biscuit overwrap"),
    ("PET film", 60, 100, 15, 20, 12, 50, "high", "low", 3, 6, True, False, False, True,
     "Bottles, trays, laminate base layer"),
    ("Metalized BOPP laminate", 1, 5, 0.5, 2, 15, 30, "medium", "high", 3, 3, False, False, False, True,
     "Namkeen, chips, biscuits - high barrier"),
    ("Aluminum foil laminate", 0.05, 0.5, 0.05, 0.5, 40, 100, "high", "high", 5, 2, False, False, False, True,
     "Retort pouches, long-shelf-life RTE, coffee"),
    ("Micro-perforated PP/LDPE film", 3000, 15000, 10, 30, 20, 40, "medium", "medium", 2, 4, True, False, True, True,
     "Fresh fruit & vegetable MAP packaging"),
    ("Kraft paper (uncoated)", 15000, 20000, 300, 500, 60, 120, "medium", "low", 1, 9, True, True, True, False,
     "Dry bakery bags, eco outer wraps (not moisture/O2 sensitive)"),
    ("PLA biodegradable film", 200, 400, 10, 20, 20, 50, "medium", "medium", 4, 8, False, True, False, True,
     "Eco-friendly short-shelf-life produce/bakery packaging"),
    ("Cellulose compostable film", 10, 50, 5, 15, 20, 40, "medium", "medium", 4, 9, False, True, False, True,
     "Premium biodegradable snack/produce wraps"),
    ("Glass jar", 0, 0, 0, 0, 0, 0, "high", "high", 4, 7, True, False, False, False,
     "Sauces, pickles, jams, retort alternative"),
]


def seed_if_empty(db: Session) -> None:
    if db.query(Commodity).count() == 0:
        for row in COMMODITIES:
            db.add(Commodity(
                name=row[0], category=row[1], moisture_pct=row[2], fat_pct=row[3], ph=row[4],
                respiration_class=row[5], oxygen_sensitive=row[6], light_sensitive=row[7],
                baseline_shelf_life_days=row[8],
            ))

    if db.query(PackagingMaterial).count() == 0:
        for row in MATERIALS:
            db.add(PackagingMaterial(
                name=row[0], otr_min=row[1], otr_max=row[2], wvtr_min=row[3], wvtr_max=row[4],
                thickness_min_um=row[5], thickness_max_um=row[6], mechanical_strength=row[7],
                sealability=row[8], cost_tier=row[9], eco_score=row[10], recyclable=row[11],
                biodegradable=row[12], breathable=row[13], map_suitable=row[14], typical_uses=row[15],
            ))

    db.commit()

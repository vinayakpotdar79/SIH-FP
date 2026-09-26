"""
Shelf-life estimator - the "light ML" layer on top of the rule engine.

Public packaging datasets linking food properties directly to measured
shelf-life outcomes do not exist in a form usable here, so this trains a
small scikit-learn regressor on a synthetic dataset generated from
literature-informed domain formulas (Q10 temperature-spoilage relationship,
oxidation/desiccation sensitivity to barrier properties, humidity effects).
This is documented deliberately as a calibrated *decision-support estimate*,
not a lab-measured prediction - see DATA_SOURCES.md.

The model is trained once at startup (a few seconds) and cached to disk with
joblib so subsequent runs load instantly.
"""

import os
import random

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor

from .models import Commodity, PackagingMaterial

MODEL_PATH = os.path.join(os.path.dirname(__file__), "data", "shelf_life_model.joblib")

RESPIRATION_ORDINAL = {"none": 0, "low": 1, "medium": 2, "high": 3}
STORAGE_ORDINAL = {"ambient": 0, "chilled": 1, "frozen": 2}

FEATURE_NAMES = [
    "respiration_ordinal", "moisture_pct", "fat_pct", "oxygen_sensitive",
    "baseline_shelf_life_days", "otr_mid", "wvtr_mid", "breathable",
    "temperature_c", "relative_humidity_pct", "storage_ordinal",
]


def _row_features(commodity: Commodity, material: PackagingMaterial, temperature_c: float,
                   relative_humidity_pct: float, storage_type: str) -> list[float]:
    otr_mid = (material.otr_min + material.otr_max) / 2.0
    wvtr_mid = (material.wvtr_min + material.wvtr_max) / 2.0
    return [
        RESPIRATION_ORDINAL[commodity.respiration_class],
        commodity.moisture_pct,
        commodity.fat_pct,
        1.0 if commodity.oxygen_sensitive else 0.0,
        commodity.baseline_shelf_life_days,
        otr_mid,
        wvtr_mid,
        1.0 if material.breathable else 0.0,
        temperature_c,
        relative_humidity_pct,
        STORAGE_ORDINAL.get(storage_type, 0),
    ]


def _synthetic_label(commodity: Commodity, material: PackagingMaterial, temperature_c: float,
                      relative_humidity_pct: float, rng: random.Random) -> float:
    otr_mid = (material.otr_min + material.otr_max) / 2.0
    wvtr_mid = (material.wvtr_min + material.wvtr_max) / 2.0

    if commodity.oxygen_sensitive:
        oxygen_factor = 1.0 + (1.0 - min(otr_mid, 8000) / 8000) * 2.0
    else:
        oxygen_factor = 1.0

    if commodity.moisture_pct > 50 or commodity.moisture_pct < 15:
        moisture_factor = 1.0 + (1.0 - min(wvtr_mid, 50) / 50) * 1.5
    else:
        moisture_factor = 1.0

    if commodity.respiration_class != "none" and not material.breathable:
        # Sealing a respiring product in a non-breathable film traps CO2/depletes O2,
        # causing anaerobic fermentation and off-flavors well before a barrier-driven
        # spoilage mechanism would apply.
        anaerobic_factor = 0.3
    else:
        anaerobic_factor = 1.0

    temp_factor = np.clip(2.0 ** ((25.0 - temperature_c) / 10.0), 0.2, 5.0)

    optimal_rh = 90 if commodity.respiration_class != "none" else 65
    rh_distance = abs(relative_humidity_pct - optimal_rh)
    rh_factor = np.clip(1.0 - rh_distance / 150.0, 0.5, 1.2)

    noise = rng.gauss(1.0, 0.08)
    shelf_life = (
        commodity.baseline_shelf_life_days * oxygen_factor * moisture_factor
        * anaerobic_factor * temp_factor * rh_factor * max(noise, 0.5)
    )
    return max(0.5, shelf_life)


def generate_training_data(commodities: list[Commodity], materials: list[PackagingMaterial],
                            samples_per_pair: int = 15, seed: int = 42):
    rng = random.Random(seed)
    X, y = [], []
    for commodity in commodities:
        for material in materials:
            for _ in range(samples_per_pair):
                temperature_c = rng.uniform(-18, 35)
                relative_humidity_pct = rng.uniform(30, 100)
                X.append(_row_features(commodity, material, temperature_c, relative_humidity_pct, "ambient"))
                y.append(_synthetic_label(commodity, material, temperature_c, relative_humidity_pct, rng))
    return np.array(X), np.array(y)


def train_or_load_model(commodities: list[Commodity], materials: list[PackagingMaterial]) -> RandomForestRegressor:
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)

    X, y = generate_training_data(commodities, materials)
    model = RandomForestRegressor(n_estimators=150, max_depth=12, random_state=42)
    model.fit(X, y)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    return model


def predict_shelf_life(model: RandomForestRegressor, commodity: Commodity, material: PackagingMaterial,
                        temperature_c: float, relative_humidity_pct: float, storage_type: str) -> float:
    features = _row_features(commodity, material, temperature_c, relative_humidity_pct, storage_type)
    prediction = model.predict(np.array([features]))[0]
    return round(float(prediction), 1)

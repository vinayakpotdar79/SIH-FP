"""
Rule-based, explainable packaging recommendation engine.

Every threshold applied here is derived from published food-packaging science
(see DATA_SOURCES.md): oxygen-sensitive / high-fat foods need low OTR to avoid
oxidative rancidity, high-moisture foods need low WVTR to avoid desiccation,
respiring fresh produce needs an OTR *matched* to its respiration rate (too
low suffocates the product; too high accelerates senescence), and so on.

The engine returns, for every candidate material, both a fit score and the
list of human-readable reasons that produced it - this trail is what gets
shown to the user as "why this material was recommended" instead of a
black-box verdict.
"""

from dataclasses import dataclass, field

from .models import Commodity, PackagingMaterial

OPAQUE_MATERIALS = {"Metalized BOPP laminate", "Aluminum foil laminate", "Kraft paper (uncoated)", "Glass jar"}

# Approximate target OTR window (cc/m2/day) for respiring fresh produce, by respiration class.
# In real production this is fine-tuned via micro-perforation density; here it is an
# illustrative reference band for decision support.
RESPIRATION_OTR_TARGET = {
    "low": (3000, 6000),
    "medium": (6000, 10000),
    "high": (10000, 16000),
}


@dataclass
class Requirement:
    max_otr: float | None = None
    otr_target_range: tuple[float, float] | None = None
    max_wvtr: float | None = None
    needs_breathable: bool = False
    needs_map: bool = False
    needs_opaque: bool = False
    needs_high_mechanical: bool = False
    reasons: list[str] = field(default_factory=list)


@dataclass
class MaterialScore:
    material: PackagingMaterial
    score: float
    reasons: list[str]


def derive_requirements(
    commodity: Commodity,
    storage_type: str,
    desired_shelf_life_days: float,
) -> Requirement:
    req = Requirement()
    is_produce = commodity.respiration_class != "none"

    if is_produce:
        lo, hi = RESPIRATION_OTR_TARGET[commodity.respiration_class]
        req.otr_target_range = (lo, hi)
        req.needs_breathable = True
        req.reasons.append(
            f"{commodity.name} keeps respiring after harvest ({commodity.respiration_class} rate), "
            f"so it needs a breathable/micro-perforated film with OTR roughly {lo:,.0f}-{hi:,.0f} "
            "cc/m2/day - not a low-OTR barrier film, which would suffocate it."
        )
        req.max_wvtr = 30
        req.reasons.append("Moderate WVTR cap keeps some transpiration allowance without excessive moisture loss.")
    else:
        if commodity.oxygen_sensitive and commodity.fat_pct > 15:
            req.max_otr = 5
            req.reasons.append(
                f"High fat content ({commodity.fat_pct}%) combined with oxygen sensitivity requires a "
                "near-zero OTR (<=5 cc/m2/day) to prevent oxidative rancidity."
            )
        elif commodity.oxygen_sensitive:
            req.max_otr = 50
            req.reasons.append(
                "Oxygen-sensitive product requires a low OTR (<=50 cc/m2/day) to limit oxidation, "
                "browning and nutrient loss."
            )

        if commodity.moisture_pct > 50:
            req.max_wvtr = 10
            req.reasons.append(
                f"High moisture content ({commodity.moisture_pct}%) requires a low WVTR (<=10 g/m2/day) "
                "to prevent desiccation/moisture loss."
            )
        elif commodity.moisture_pct < 15:
            req.max_wvtr = 10
            req.reasons.append(
                f"Low moisture content ({commodity.moisture_pct}%) requires a low WVTR (<=10 g/m2/day) "
                "to prevent moisture ingress, staling and loss of crispness."
            )
        else:
            req.max_wvtr = 15
            req.reasons.append("Moderate moisture content requires a moderate WVTR cap (<=15 g/m2/day).")

    if commodity.oxygen_sensitive and desired_shelf_life_days > commodity.baseline_shelf_life_days * 2:
        req.needs_map = True
        req.reasons.append(
            f"Target shelf life ({desired_shelf_life_days:.0f} days) is more than double the baseline "
            f"({commodity.baseline_shelf_life_days:.0f} days) for this product, so Modified Atmosphere "
            "Packaging is recommended to reach it."
        )

    if commodity.light_sensitive:
        req.needs_opaque = True
        req.reasons.append(f"{commodity.name} is light-sensitive, so an opaque or metalized/foil layer is preferred.")

    if storage_type == "frozen":
        req.needs_high_mechanical = True
        req.reasons.append("Frozen storage requires high mechanical strength to survive freeze-thaw handling.")

    return req


def _range_midpoint(lo: float, hi: float) -> float:
    return (lo + hi) / 2.0


def score_material(material: PackagingMaterial, req: Requirement) -> MaterialScore:
    score = 100.0
    reasons: list[str] = []

    if req.needs_breathable:
        if not material.breathable:
            score -= 60
            reasons.append(f"Not breathable/micro-perforated - unsuitable for a respiring product.")
        else:
            lo, hi = req.otr_target_range
            mid = _range_midpoint(material.otr_min, material.otr_max)
            if lo <= mid <= hi:
                reasons.append(f"OTR range ({material.otr_min:.0f}-{material.otr_max:.0f}) matches the required respiration window.")
            else:
                distance = min(abs(mid - lo), abs(mid - hi))
                score -= min(40, distance / 200)
                reasons.append("OTR range is outside the ideal respiration window.")
    elif req.max_otr is not None:
        mid = _range_midpoint(material.otr_min, material.otr_max)
        if mid <= req.max_otr:
            reasons.append(f"OTR ({material.otr_min:.1f}-{material.otr_max:.1f} cc/m2/day) meets the required <= {req.max_otr} cap.")
        else:
            score -= 40
            reasons.append(f"OTR ({material.otr_min:.1f}-{material.otr_max:.1f}) exceeds the required <= {req.max_otr} cap.")

    if req.max_wvtr is not None:
        mid = _range_midpoint(material.wvtr_min, material.wvtr_max)
        if mid <= req.max_wvtr:
            reasons.append(f"WVTR ({material.wvtr_min:.1f}-{material.wvtr_max:.1f} g/m2/day) meets the required <= {req.max_wvtr} cap.")
        else:
            score -= 30
            reasons.append(f"WVTR ({material.wvtr_min:.1f}-{material.wvtr_max:.1f}) exceeds the required <= {req.max_wvtr} cap.")

    if req.needs_map and not material.map_suitable:
        score -= 25
        reasons.append("Not typically used for Modified Atmosphere Packaging.")

    if req.needs_opaque and material.name not in OPAQUE_MATERIALS:
        score -= 10
        reasons.append("Mostly transparent - would need an added opaque/UV-blocking layer for a light-sensitive product.")

    if req.needs_high_mechanical and material.mechanical_strength != "high":
        score -= 15
        reasons.append("Mechanical strength may be insufficient for frozen handling.")

    return MaterialScore(material=material, score=max(0.0, score), reasons=reasons)


def recommend(
    commodity: Commodity,
    materials: list[PackagingMaterial],
    storage_type: str,
    desired_shelf_life_days: float,
    top_n: int = 3,
) -> tuple[Requirement, list[MaterialScore]]:
    req = derive_requirements(commodity, storage_type, desired_shelf_life_days)
    scored = [score_material(m, req) for m in materials]
    scored.sort(key=lambda s: s.score, reverse=True)
    return req, scored[:top_n]

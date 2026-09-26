"""
Modified Atmosphere Packaging (MAP) gas-mix + shelf-life-extension calculator
for respiring fresh produce.

The gas-mix targets and shelf-life multipliers are illustrative, literature-
informed reference bands (see DATA_SOURCES.md), not certified values for a
specific cultivar/batch. The temperature adjustment uses a simplified Q10
(~2x spoilage rate per 10C) model anchored at a 4C chilled reference point,
which is the standard first-order approximation used in post-harvest
handling literature for demo/decision-support purposes.
"""

from dataclasses import dataclass

from .models import Commodity

GAS_MIX_TARGETS = {
    "low": {"o2": (5, 10), "co2": (3, 5)},
    "medium": {"o2": (3, 7), "co2": (5, 10)},
    "high": {"o2": (2, 5), "co2": (5, 15)},
}

BASE_SHELF_LIFE_MULTIPLIER = {"low": 1.5, "medium": 2.0, "high": 2.5}

Q10 = 2.0  # spoilage rate roughly doubles every 10C rise (simplified first-order approximation)
REFERENCE_TEMP_C = 4.0
OPTIMAL_RH_RANGE = (85, 95)


@dataclass
class MapResult:
    applicable: bool
    o2_pct: tuple[float, float] | None = None
    co2_pct: tuple[float, float] | None = None
    n2_note: str = "Balance made up with nitrogen (N2)."
    base_shelf_life_days: float = 0.0
    map_shelf_life_days: float = 0.0
    temperature_adjusted_days: float = 0.0
    humidity_factor: float = 1.0
    reasons: list[str] = None


def calculate_map(commodity: Commodity, temperature_c: float, relative_humidity_pct: float) -> MapResult:
    if commodity.respiration_class == "none":
        return MapResult(
            applicable=False,
            reasons=[f"{commodity.name} does not respire post-harvest, so MAP gas-mix optimization does not apply."],
        )

    reasons: list[str] = []
    targets = GAS_MIX_TARGETS[commodity.respiration_class]
    multiplier = BASE_SHELF_LIFE_MULTIPLIER[commodity.respiration_class]

    map_shelf_life = commodity.baseline_shelf_life_days * multiplier
    reasons.append(
        f"{commodity.respiration_class.title()}-respiration produce: recommended in-pack mix is "
        f"O2 {targets['o2'][0]}-{targets['o2'][1]}%, CO2 {targets['co2'][0]}-{targets['co2'][1]}%, "
        f"balance N2 - typically extending shelf life ~{multiplier:.1f}x over unmodified atmosphere."
    )

    temp_delta = REFERENCE_TEMP_C - temperature_c
    temp_factor = Q10 ** (temp_delta / 10.0)
    temperature_adjusted_days = map_shelf_life * temp_factor
    if temperature_c > REFERENCE_TEMP_C:
        reasons.append(
            f"Storage at {temperature_c:.1f}C (above the {REFERENCE_TEMP_C:.0f}C chilled reference) "
            f"roughly speeds up spoilage, reducing the estimate to ~{temperature_adjusted_days:.1f} days."
        )
    elif temperature_c < REFERENCE_TEMP_C:
        reasons.append(
            f"Storage at {temperature_c:.1f}C (below the {REFERENCE_TEMP_C:.0f}C chilled reference) "
            f"slows spoilage further, extending the estimate to ~{temperature_adjusted_days:.1f} days "
            "(watch for chilling injury on tropical produce)."
        )

    lo_rh, hi_rh = OPTIMAL_RH_RANGE
    if lo_rh <= relative_humidity_pct <= hi_rh:
        humidity_factor = 1.0
    else:
        distance = min(abs(relative_humidity_pct - lo_rh), abs(relative_humidity_pct - hi_rh))
        humidity_factor = max(0.6, 1.0 - distance / 100.0)
        reasons.append(
            f"Relative humidity {relative_humidity_pct:.0f}% is outside the optimal "
            f"{lo_rh}-{hi_rh}% band, which trims the estimate by "
            f"{(1 - humidity_factor) * 100:.0f}% (moisture loss or condensation/decay risk)."
        )

    final_days = temperature_adjusted_days * humidity_factor

    return MapResult(
        applicable=True,
        o2_pct=targets["o2"],
        co2_pct=targets["co2"],
        base_shelf_life_days=commodity.baseline_shelf_life_days,
        map_shelf_life_days=round(map_shelf_life, 1),
        temperature_adjusted_days=round(final_days, 1),
        humidity_factor=round(humidity_factor, 2),
        reasons=reasons,
    )

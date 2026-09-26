# Data sources & assumptions

This prototype's knowledge base (`backend/app/seed_data.py`) uses representative
reference ranges compiled from public food-packaging science literature. They are
for **decision-support demonstration purposes**, not certified lab measurements
for a specific product batch, cultivar, or supplier's exact film grade.

## Commodity properties (moisture %, fat %, pH, respiration class, baseline shelf life)
- FAO post-harvest handling and produce compendium guidance for fresh fruit &
  vegetable respiration rates and typical ambient shelf life.
- Standard food composition references for moisture/fat/pH of common commodities
  (dairy, meat, bakery, snacks, spices).

## Packaging material barrier properties (OTR, WVTR, thickness, mechanical strength)
- Published permeability tables for common food-packaging films (LDPE, HDPE, PP,
  PET, metalized/foil laminates, biodegradable films) as commonly cited in food
  packaging engineering references and datasheets.
- Ranges are deliberately kept as bands (min-max) rather than single values,
  reflecting the real variability across thickness/grade/supplier.

## MAP gas-mix targets and shelf-life multipliers
- Illustrative bands drawn from general Modified Atmosphere Packaging guidance
  for produce categories grouped by respiration rate (low/medium/high).
  Real MAP design work fine-tunes these per cultivar/cultivar-lot and validates
  with a sealed-pack O2/CO2 trial - this prototype's numbers are a first-pass
  decision-support estimate, explicitly framed as such in the UI.

## Shelf-life regression model
- No public dataset exists mapping (food properties x packaging barrier
  properties x storage conditions) -> measured shelf life in a form usable
  here. The model in `backend/app/shelf_life_model.py` is trained on a
  **synthetic dataset generated from documented domain formulas**: a Q10
  (~2x spoilage rate per 10C) temperature relationship, an oxidation-sensitivity
  response to OTR for high-fat/oxygen-sensitive foods, and a desiccation
  response to WVTR for high/low-moisture foods. This is disclosed in the UI
  and in the code as a calibrated estimate, not a lab-measured prediction -
  the honest framing is intentional and should be stated as such in any pitch
  to judges.

## Sustainability / eco-score and cost tier
- Recyclability and biodegradability flags reflect widely known material
  properties (e.g., mono-material PE/PET streams are recyclable in most
  municipal systems; multilayer metalized/foil laminates are not; PLA/cellulose
  are compostable under industrial conditions, not standard recycling streams).
- Cost tiers (1-5) are relative orderings based on typical market cost per unit
  area, not live pricing.

## Extending this with real data
For a production system, replace `seed_data.py` with sourced values from:
FSSAI packaging guidance, IS packaging standards, supplier datasheets (for
exact OTR/WVTR by grade/thickness), and in-house or published shelf-life
trial data. The rule engine and ML layer are structured so that only the
seed data and the shelf-life training set need to change - the recommendation
logic and MAP calculator stay the same.

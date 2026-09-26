from pydantic import BaseModel


class CommodityOut(BaseModel):
    id: int
    name: str
    category: str
    moisture_pct: float
    fat_pct: float
    ph: float
    respiration_class: str
    oxygen_sensitive: bool
    light_sensitive: bool
    baseline_shelf_life_days: float

    class Config:
        from_attributes = True


class MaterialOut(BaseModel):
    id: int
    name: str
    otr_min: float
    otr_max: float
    wvtr_min: float
    wvtr_max: float
    thickness_min_um: float
    thickness_max_um: float
    mechanical_strength: str
    sealability: str
    cost_tier: int
    eco_score: int
    recyclable: bool
    biodegradable: bool
    breathable: bool
    map_suitable: bool
    typical_uses: str

    class Config:
        from_attributes = True


class RecommendRequest(BaseModel):
    commodity_id: int
    storage_type: str  # ambient, chilled, frozen
    desired_shelf_life_days: float
    temperature_c: float
    relative_humidity_pct: float


class MaterialRecommendation(BaseModel):
    material: MaterialOut
    score: float
    reasons: list[str]
    predicted_shelf_life_days: float


class MapInfo(BaseModel):
    applicable: bool
    o2_pct: tuple[float, float] | None = None
    co2_pct: tuple[float, float] | None = None
    n2_note: str | None = None
    base_shelf_life_days: float | None = None
    map_shelf_life_days: float | None = None
    temperature_adjusted_days: float | None = None
    humidity_factor: float | None = None
    reasons: list[str] = []


class RecommendResponse(BaseModel):
    commodity: CommodityOut
    requirement_reasons: list[str]
    recommendations: list[MaterialRecommendation]
    map_info: MapInfo
    passport_id: str
    qr_data_uri: str


class ShelfLifeCurveRequest(BaseModel):
    commodity_id: int
    material_id: int
    storage_type: str
    relative_humidity_pct: float


class ShelfLifeCurvePoint(BaseModel):
    temperature_c: float
    predicted_shelf_life_days: float


class PassportOut(BaseModel):
    passport_id: str
    commodity_name: str
    created_at: str
    result: dict

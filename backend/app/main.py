import json

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import map_calculator, recommendation_engine, schemas, shelf_life_model
from .database import Base, SessionLocal, engine, get_db
from .models import Commodity, PackagingMaterial, Recommendation
from .qr_service import generate_qr_data_uri
from .seed_data import seed_if_empty

app = FastAPI(title="Intelligent Food Packaging Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_PASSPORT_BASE_URL = "http://localhost:5173/passport"


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
        commodities = db.query(Commodity).all()
        materials = db.query(PackagingMaterial).all()
        app.state.shelf_life_model = shelf_life_model.train_or_load_model(commodities, materials)
    finally:
        db.close()


@app.get("/api/commodities", response_model=list[schemas.CommodityOut])
def list_commodities(db: Session = Depends(get_db)):
    return db.query(Commodity).order_by(Commodity.name).all()


@app.get("/api/materials", response_model=list[schemas.MaterialOut])
def list_materials(db: Session = Depends(get_db)):
    return db.query(PackagingMaterial).order_by(PackagingMaterial.name).all()


@app.post("/api/recommend", response_model=schemas.RecommendResponse)
def recommend(payload: schemas.RecommendRequest, db: Session = Depends(get_db)):
    commodity = db.query(Commodity).filter(Commodity.id == payload.commodity_id).first()
    if not commodity:
        raise HTTPException(status_code=404, detail="Commodity not found")

    materials = db.query(PackagingMaterial).all()

    req, scored = recommendation_engine.recommend(
        commodity=commodity,
        materials=materials,
        storage_type=payload.storage_type,
        desired_shelf_life_days=payload.desired_shelf_life_days,
    )

    map_result = map_calculator.calculate_map(
        commodity=commodity,
        temperature_c=payload.temperature_c,
        relative_humidity_pct=payload.relative_humidity_pct,
    )

    material_recs = []
    for entry in scored:
        predicted_days = shelf_life_model.predict_shelf_life(
            app.state.shelf_life_model,
            commodity=commodity,
            material=entry.material,
            temperature_c=payload.temperature_c,
            relative_humidity_pct=payload.relative_humidity_pct,
            storage_type=payload.storage_type,
        )
        material_recs.append(schemas.MaterialRecommendation(
            material=schemas.MaterialOut.model_validate(entry.material),
            score=round(entry.score, 1),
            reasons=entry.reasons,
            predicted_shelf_life_days=predicted_days,
        ))

    map_info = schemas.MapInfo(
        applicable=map_result.applicable,
        o2_pct=map_result.o2_pct,
        co2_pct=map_result.co2_pct,
        n2_note=map_result.n2_note if map_result.applicable else None,
        base_shelf_life_days=map_result.base_shelf_life_days if map_result.applicable else None,
        map_shelf_life_days=map_result.map_shelf_life_days if map_result.applicable else None,
        temperature_adjusted_days=map_result.temperature_adjusted_days if map_result.applicable else None,
        humidity_factor=map_result.humidity_factor if map_result.applicable else None,
        reasons=map_result.reasons or [],
    )

    result_payload = {
        "commodity": schemas.CommodityOut.model_validate(commodity).model_dump(),
        "requirement_reasons": req.reasons,
        "recommendations": [r.model_dump() for r in material_recs],
        "map_info": map_info.model_dump(),
    }

    record = Recommendation(
        commodity_name=commodity.name,
        inputs_json=json.dumps(payload.model_dump()),
        result_json=json.dumps(result_payload, default=str),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    qr_data_uri = generate_qr_data_uri(f"{FRONTEND_PASSPORT_BASE_URL}/{record.passport_id}")

    return schemas.RecommendResponse(
        commodity=schemas.CommodityOut.model_validate(commodity),
        requirement_reasons=req.reasons,
        recommendations=material_recs,
        map_info=map_info,
        passport_id=record.passport_id,
        qr_data_uri=qr_data_uri,
    )


@app.post("/api/shelf-life-curve", response_model=list[schemas.ShelfLifeCurvePoint])
def shelf_life_curve(payload: schemas.ShelfLifeCurveRequest, db: Session = Depends(get_db)):
    commodity = db.query(Commodity).filter(Commodity.id == payload.commodity_id).first()
    material = db.query(PackagingMaterial).filter(PackagingMaterial.id == payload.material_id).first()
    if not commodity or not material:
        raise HTTPException(status_code=404, detail="Commodity or material not found")

    temps = range(-20, 41, 5)
    points = []
    for temp in temps:
        predicted = shelf_life_model.predict_shelf_life(
            app.state.shelf_life_model,
            commodity=commodity,
            material=material,
            temperature_c=float(temp),
            relative_humidity_pct=payload.relative_humidity_pct,
            storage_type=payload.storage_type,
        )
        points.append(schemas.ShelfLifeCurvePoint(temperature_c=float(temp), predicted_shelf_life_days=predicted))
    return points


@app.get("/api/passport/{passport_id}", response_model=schemas.PassportOut)
def get_passport(passport_id: str, db: Session = Depends(get_db)):
    record = db.query(Recommendation).filter(Recommendation.passport_id == passport_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Passport not found")

    return schemas.PassportOut(
        passport_id=record.passport_id,
        commodity_name=record.commodity_name,
        created_at=record.created_at.isoformat(),
        result=json.loads(record.result_json),
    )

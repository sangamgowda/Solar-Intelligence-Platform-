import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect

from src.core.config import settings
from src.db.session import SessionLocal, engine
from src.db.base import Base
from src.api.v1.router import api_router
from src.services.backfill_service import backfill_data

# Setup logging
logging.basicConfig(level=logging.INFO)

def setup_db():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if "solar_predictions" in existing_tables:
        logging.info("Old 'solar_predictions' table found. Dropping all tables for migration.")
        Base.metadata.drop_all(bind=engine)
    
    Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
def startup_event():
    setup_db()
    db = SessionLocal()
    try:
        backfill_data(db)
    finally:
        db.close()

@app.get("/status")
def get_status():
    return {"status": "running", "time": datetime.now().isoformat()}

# Keeping the old root endpoints for backwards compatibility temporarily
from src.api.v1.endpoints.weather import get_current_weather
from src.api.v1.endpoints.predictions import get_predictions, trigger_day
from src.api.v1.endpoints.analytics import get_model_performance

app.add_api_route("/current-weather", get_current_weather, methods=["GET"])
app.add_api_route("/predictions", get_predictions, methods=["GET"])
app.add_api_route("/trigger-day", trigger_day, methods=["POST"])
app.add_api_route("/analytics/model-performance", get_model_performance, methods=["GET"])

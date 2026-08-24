from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

class WeatherCurrentResponse(BaseModel):
    temperature: float
    humidity: float
    wind_speed: float
    timestamp: str

class PredictionData(BaseModel):
    id: int
    timestamp: datetime
    ghi: float
    power: float
    temperature: float
    humidity: float
    wind_speed: float
    # Omitting all features to keep it readable, but config allows ORM
    model_config = ConfigDict(from_attributes=True)

class ModelSummary(BaseModel):
    data: List[PredictionData]
    summary_mwh: float

class PredictionsResponse(BaseModel):
    view_mode: str
    range_days: int
    is_today: bool
    yesterday_date: str
    tomorrow_date: str
    target_date_label: str
    target_date_iso: str
    lstm: ModelSummary
    lgbm: ModelSummary
    actual: ModelSummary

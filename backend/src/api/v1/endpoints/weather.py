from fastapi import APIRouter
from datetime import datetime
import logging
from src.services.prediction_service import fetch_weather_data, LAT, LON

router = APIRouter()

@router.get("/current-weather")
def get_current_weather():
    """Fetch truly live weather data for the current hour."""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    try:
        df = fetch_weather_data(LAT, LON, date_str, date_str, use_archive=False)
        current_hour = now.hour
        if current_hour >= len(df):
            current_hour = len(df) - 1
        row = df.iloc[current_hour]
        return {
            "temperature": float(row["temperature"]),
            "humidity": float(row["humidity"]),
            "wind_speed": float(row["wind_speed"]),
            "timestamp": row["timestamp"].isoformat()
        }
    except Exception as e:
        logging.error(f"Error fetching current weather: {e}")
        return {"error": str(e)}

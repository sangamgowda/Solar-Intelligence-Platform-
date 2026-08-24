from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from src.db.session import get_db
from src.db.models import LSTMPrediction, LGBMPrediction, ActualData
from src.services.prediction_service import predict_lstm_for_day, predict_lgbm_for_day
from src.schemas.prediction import PredictionsResponse

router = APIRouter()

@router.get("/", response_model=PredictionsResponse)
def get_predictions(view_mode: str = "forecast", range_days: int = 1, date: str = None, db: Session = Depends(get_db)):
    """Fetch analytics data for Forecast (Tomorrow ONLY) or Past (Yesterday/Custom history)."""
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    if view_mode == "forecast":
        start_dt = datetime.combine(tomorrow, datetime.min.time())
        end_dt = datetime.combine(tomorrow, datetime.max.time())
        summary_date = tomorrow
    else:
        base_date = yesterday
        if date:
            try:
                base_date = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                logging.warning(f"Invalid date format: {date}. Using yesterday.")
        
        start_date = base_date - timedelta(days=range_days - 1)
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(base_date, datetime.max.time())
        summary_date = base_date

    lstm_data = db.query(LSTMPrediction).filter(
        LSTMPrediction.timestamp >= start_dt, LSTMPrediction.timestamp <= end_dt
    ).order_by(LSTMPrediction.timestamp.asc()).all()

    lgbm_data = db.query(LGBMPrediction).filter(
        LGBMPrediction.timestamp >= start_dt, LGBMPrediction.timestamp <= end_dt
    ).order_by(LGBMPrediction.timestamp.asc()).all()

    actual_data = db.query(ActualData).filter(
        ActualData.timestamp >= start_dt, ActualData.timestamp <= end_dt
    ).order_by(ActualData.timestamp.asc()).all()

    def get_summary(data_list, view_m, range_d):
        if view_m == "past" and range_d > 1:
            return sum([p.power for p in data_list])
        return sum([p.power for p in data_list if p.timestamp.date() == summary_date])

    return {
        "view_mode": view_mode,
        "range_days": range_days,
        "is_today": view_mode == "forecast",
        "yesterday_date": yesterday.strftime("%b %d, %Y"),
        "tomorrow_date": tomorrow.strftime("%b %d, %Y"),
        "target_date_label": summary_date.strftime("%b %d, %Y"),
        "target_date_iso": summary_date.isoformat(),
        "lstm": {
            "data": lstm_data,
            "summary_mwh": get_summary(lstm_data, view_mode, range_days)
        },
        "lgbm": {
            "data": lgbm_data,
            "summary_mwh": get_summary(lgbm_data, view_mode, range_days)
        },
        "actual": {
            "data": actual_data,
            "summary_mwh": get_summary(actual_data, view_mode, range_days)
        }
    }

@router.post("/trigger-day")
def trigger_day(date: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Manually trigger prediction for both models."""
    background_tasks.add_task(predict_lstm_for_day, date)
    background_tasks.add_task(predict_lgbm_for_day, date)
    return {"message": f"Prediction tasks for {date} added to background for both models"}

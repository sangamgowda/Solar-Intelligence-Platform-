import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.core.config import settings
from src.db.models import ActualData, LSTMPrediction, LGBMPrediction
from src.services.prediction_service import fetch_actual_data_for_day, predict_lstm_for_day, predict_lgbm_for_day

def _populate_table(db: Session, model_class, df, date_str, source_name):
    try:
        for _, row in df.iterrows():
            ghi_val = row['ghi'] if source_name == 'Actual' else row['ghi_pred']
            db.add(model_class(
                timestamp=row['timestamp'].to_pydatetime(),
                temperature=row['temperature'],
                humidity=row['humidity'],
                wind_speed=row['wind_speed'],
                wind_direction=row['wind_direction'],
                surface_pressure=row['surface_pressure'],
                cloud_cover=row['cloud_cover'],
                water_vapour=row['water_vapour'],
                dni=row['dni'],
                dhi=row['dhi'],
                ghi=ghi_val,
                power=row['power'],
                kt=row['kt'],
                solar_zenith=row['solar_zenith'],
                cos_zenith=row['cos_zenith'],
                clear_ghi=row['clear_ghi'],
                ghi_clear_weighted=row['ghi_clear_weighted'],
                hour_sin=row['hour_sin'],
                hour_cos=row['hour_cos'],
                day_sin=row['day_sin'],
                day_cos=row['day_cos']
            ))
        db.commit()
    except Exception as e:
        logging.error(f"{source_name} Backfill Error {date_str}: {e}")
        db.rollback()

def backfill_data(db: Session):
    start_date = settings.PROJECT_START_DATE
    end_date = datetime.now() + timedelta(days=1)
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        day_start = datetime.combine(current_date.date(), datetime.min.time())
        day_end = day_start + timedelta(days=1)
        
        # Actual
        if current_date.date() < datetime.now().date():
            exists = db.query(ActualData).filter(ActualData.timestamp >= day_start, ActualData.timestamp < day_end).first()
            if not exists:
                df = fetch_actual_data_for_day(date_str)
                _populate_table(db, ActualData, df, date_str, 'Actual')

        # LSTM
        exists = db.query(LSTMPrediction).filter(LSTMPrediction.timestamp >= day_start, LSTMPrediction.timestamp < day_end).first()
        if not exists:
            df = predict_lstm_for_day(date_str)
            _populate_table(db, LSTMPrediction, df, date_str, 'LSTM')

        # LGBM
        exists = db.query(LGBMPrediction).filter(LGBMPrediction.timestamp >= day_start, LGBMPrediction.timestamp < day_end).first()
        if not exists:
            df = predict_lgbm_for_day(date_str)
            _populate_table(db, LGBMPrediction, df, date_str, 'LGBM')

        current_date += timedelta(days=1)

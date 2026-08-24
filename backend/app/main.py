from fastapi import FastAPI, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from . import models, prediction, database
from .database import SessionLocal, engine

# Initialize Database
PROJECT_START_DATE = datetime(2026, 1, 1)

def setup_db():
    from sqlalchemy import inspect
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if "solar_predictions" in existing_tables:
        logging.info("Old 'solar_predictions' table found. Dropping all tables for migration.")
        models.Base.metadata.drop_all(bind=engine)
    
    models.init_db()

setup_db()

app = FastAPI(title="Solar Power Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def backfill_data(db: Session):
    """Populate database for both LSTM and LGBM from PROJECT_START_DATE to Tomorrow."""
    start_date = PROJECT_START_DATE
    end_date = datetime.now() + timedelta(days=1)
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        day_start = datetime.combine(current_date.date(), datetime.min.time())
        day_end = day_start + timedelta(days=1)
        # Actual Data Backfill (Up to Yesterday)
        if current_date.date() < datetime.now().date():
            exists_actual = db.query(models.ActualData).filter(
                models.ActualData.timestamp >= day_start,
                models.ActualData.timestamp < day_end
            ).first()
            if not exists_actual:
                try:
                    results = prediction.fetch_actual_data_for_day(date_str)
                    for _, row in results.iterrows():
                        db.add(models.ActualData(
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
                            ghi=row['ghi'],
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
                    logging.error(f"Actual Error {date_str}: {e}")
                    db.rollback()

        # LSTM Backfill
        exists_lstm = db.query(models.LSTMPrediction).filter(
            models.LSTMPrediction.timestamp >= day_start,
            models.LSTMPrediction.timestamp < day_end
        ).first()
        if not exists_lstm:
            try:
                results = prediction.predict_lstm_for_day(date_str)
                for _, row in results.iterrows():
                    db.add(models.LSTMPrediction(
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
                        ghi=row['ghi_pred'],
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
                logging.error(f"LSTM Error {date_str}: {e}")
                db.rollback()

        # LGBM Backfill
        exists_lgbm = db.query(models.LGBMPrediction).filter(
            models.LGBMPrediction.timestamp >= day_start,
            models.LGBMPrediction.timestamp < day_end
        ).first()
        if not exists_lgbm:
            try:
                results = prediction.predict_lgbm_for_day(date_str)
                for _, row in results.iterrows():
                    db.add(models.LGBMPrediction(
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
                        ghi=row['ghi_pred'],
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
                logging.error(f"LGBM Error {date_str}: {e}")
                db.rollback()
        
        current_date += timedelta(days=1)

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        backfill_data(db)
    finally:
        db.close()

from sqlalchemy import func

@app.get("/current-weather")
def get_current_weather():
    """Fetch truly live weather data for the current hour."""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    try:
        df = prediction.fetch_weather_data(prediction.LAT, prediction.LON, date_str, date_str, use_archive=False)
        current_hour = now.hour
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

@app.get("/predictions")
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

    # Data Queries
    lstm_data = db.query(models.LSTMPrediction).filter(
        models.LSTMPrediction.timestamp >= start_dt,
        models.LSTMPrediction.timestamp <= end_dt
    ).order_by(models.LSTMPrediction.timestamp.asc()).all()

    lgbm_data = db.query(models.LGBMPrediction).filter(
        models.LGBMPrediction.timestamp >= start_dt,
        models.LGBMPrediction.timestamp <= end_dt
    ).order_by(models.LGBMPrediction.timestamp.asc()).all()

    actual_data = db.query(models.ActualData).filter(
        models.ActualData.timestamp >= start_dt,
        models.ActualData.timestamp <= end_dt
    ).order_by(models.ActualData.timestamp.asc()).all()

    # Summaries for the primary cards
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

@app.post("/trigger-day")
def trigger_day(date: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Manually trigger prediction for both models."""
    background_tasks.add_task(prediction.predict_lstm_for_day, date)
    background_tasks.add_task(prediction.predict_lgbm_for_day, date)
    return {"message": f"Prediction tasks for {date} added to background for both models"}

@app.get("/status")
def get_status():
    return {"status": "running", "time": datetime.now()}

@app.get("/analytics/model-performance")
def get_model_performance(db: Session = Depends(get_db)):
    """Fetch aggregated performance metrics for all models since project start."""
    
    # Query daily sums for all models
    daily_actual = db.query(
        func.date(models.ActualData.timestamp).label("date"),
        func.sum(models.ActualData.power).label("total_power")
    ).group_by(func.date(models.ActualData.timestamp)).all()
    
    daily_lstm = db.query(
        func.date(models.LSTMPrediction.timestamp).label("date"),
        func.sum(models.LSTMPrediction.power).label("total_power")
    ).group_by(func.date(models.LSTMPrediction.timestamp)).all()
    
    daily_lgbm = db.query(
        func.date(models.LGBMPrediction.timestamp).label("date"),
        func.sum(models.LGBMPrediction.power).label("total_power")
    ).group_by(func.date(models.LGBMPrediction.timestamp)).all()

    # Convert to maps for easy lookup
    actual_map = {str(d.date): float(d.total_power) for d in daily_actual}
    lstm_map = {str(d.date): float(d.total_power) for d in daily_lstm}
    lgbm_map = {str(d.date): float(d.total_power) for d in daily_lgbm}

    all_dates = sorted(list(set(actual_map.keys()) | set(lstm_map.keys()) | set(lgbm_map.keys())))
    
    table_data = []
    for date_str in all_dates:
        actual = actual_map.get(date_str, 0)
        lstm = lstm_map.get(date_str, 0)
        lgbm = lgbm_map.get(date_str, 0)
        
        variation_lstm = abs(actual - lstm) if actual > 0 else 0
        variation_lgbm = abs(actual - lgbm) if actual > 0 else 0
        
        def calc_acc(act, pred):
            if act == 0: return 100.0 if pred == 0 else 0.0
            error = abs(act - pred) / act
            return max(0, 100.0 * (1.0 - error))

        table_data.append({
            "date": date_str,
            "actual": actual,
            "lstm": lstm,
            "lgbm": lgbm,
            "variation_lstm": variation_lstm,
            "variation_lgbm": variation_lgbm,
            "accuracy_lstm": calc_acc(actual, lstm),
            "accuracy_lgbm": calc_acc(actual, lgbm)
        })

    # Stats Summary
    valid_acc_lstm = [d["accuracy_lstm"] for d in table_data if d["actual"] > 0]
    valid_acc_lgbm = [d["accuracy_lgbm"] for d in table_data if d["actual"] > 0]
    
    overall_acc_lstm = sum(valid_acc_lstm) / len(valid_acc_lstm) if valid_acc_lstm else 0
    overall_acc_lgbm = sum(valid_acc_lgbm) / len(valid_acc_lgbm) if valid_acc_lgbm else 0
    
    recent_actual = [d for d in table_data if d["actual"] > 0]
    last_day_stats = recent_actual[-1] if recent_actual else None

    return {
        "summary": {
            "lstm": {
                "overall_accuracy": overall_acc_lstm,
                "today_accuracy": last_day_stats["accuracy_lstm"] if last_day_stats else 0,
                "description": "Long Short-Term Memory (LSTM) - A Deep Learning recurrent neural network architecture capable of learning long-term dependencies, optimized for time-series solar GHI forecasting."
            },
            "lgbm": {
                "overall_accuracy": overall_acc_lgbm,
                "today_accuracy": last_day_stats["accuracy_lgbm"] if last_day_stats else 0,
                "description": "Light Gradient Boosting Machine (LGBM) - A high-performance Gradient Boosting framework that uses tree-based learning algorithms, effectively capturing non-linear patterns in environmental data."
            }
        },
        "table_data": table_data
    }

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.db.session import get_db
from src.db.models import ActualData, LSTMPrediction, LGBMPrediction

router = APIRouter()

@router.get("/model-performance")
def get_model_performance(db: Session = Depends(get_db)):
    """Fetch aggregated performance metrics for all models since project start."""
    daily_actual = db.query(
        func.date(ActualData.timestamp).label("date"),
        func.sum(ActualData.power).label("total_power")
    ).group_by(func.date(ActualData.timestamp)).all()
    
    daily_lstm = db.query(
        func.date(LSTMPrediction.timestamp).label("date"),
        func.sum(LSTMPrediction.power).label("total_power")
    ).group_by(func.date(LSTMPrediction.timestamp)).all()
    
    daily_lgbm = db.query(
        func.date(LGBMPrediction.timestamp).label("date"),
        func.sum(LGBMPrediction.power).label("total_power")
    ).group_by(func.date(LGBMPrediction.timestamp)).all()

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

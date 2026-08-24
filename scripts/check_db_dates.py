from app.database import SessionLocal
from app.models import ActualData, LSTMPrediction, LGBMPrediction
from sqlalchemy import func

def check_dates():
    session = SessionLocal()
    try:
        def get_range(model):
            min_ts = session.query(func.min(model.timestamp)).scalar()
            max_ts = session.query(func.max(model.timestamp)).scalar()
            return min_ts, max_ts

        print("ActualData range:", get_range(ActualData))
        print("LSTMPrediction range:", get_range(LSTMPrediction))
        print("LGBMPrediction range:", get_range(LGBMPrediction))
    finally:
        session.close()

if __name__ == "__main__":
    check_dates()

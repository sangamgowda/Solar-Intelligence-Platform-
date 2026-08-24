import os
import pandas as pd
from datetime import datetime

# Import from app package
from app import prediction

def test():
    print(f"LGBM Features defined in models: {prediction.lgbm_features}")
    print(f"Number of LGBM features: {len(prediction.lgbm_features)}")
    
    date_str = "2026-02-10"
    print(f"Testing LSTM for {date_str}...")
    try:
        res_lstm = prediction.predict_lstm_for_day(date_str)
        print("LSTM Success!")
        print(res_lstm[['timestamp', 'ghi_pred', 'power']].head())
        print(f"Total LSTM Power: {res_lstm['power'].sum():.4f} MWh")
    except Exception as e:
        print(f"LSTM Failed: {e}")
        import traceback
        traceback.print_exc()

    print(f"\nTesting LGBM for {date_str}...")
    try:
        res_lgbm = prediction.predict_lgbm_for_day(date_str)
        print("LGBM Success!")
        print(res_lgbm[['timestamp', 'ghi_pred', 'power']].head())
        print(f"Total LGBM Power: {res_lgbm['power'].sum():.4f} MWh")
    except Exception as e:
        print(f"LGBM Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()

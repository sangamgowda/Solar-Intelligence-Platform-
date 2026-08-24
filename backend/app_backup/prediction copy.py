import os
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from datetime import datetime, timedelta
import openmeteo_requests
import requests_cache
from retry_requests import retry
from .utils import add_solar_features_ist

# Constants for Power Calculation
PLANT_CAPACITY_MW = 1.0
PV_AREA = 2.833
NO_PANELS = 2318
TOTAL_PV_AREA = PV_AREA * NO_PANELS
PV_EFFICIENCY = 0.21
DERATE = 0.90
NOCT = 42
TEMP_COEFF = -0.004
SUN_ELEVATION_LIMIT = 5
TILT = 12

LAT = 10.7905
LON = 78.7047
SEQ_LEN = 48
HORIZON = 24

FEATURES = [
    "kt", "solar_zenith", "cos_zenith", "cloud_cover",
    "temperature", "humidity", "wind_speed", "surface_pressure",
    "clear_ghi", "wind_direction", "water_vapour",
    "dni", "dhi", "hour_sin", "hour_cos",
    "day_sin", "day_cos", "ghi_clear_weighted"
]

# Paths to models
APP_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(os.path.dirname(APP_DIR), "models")

LSTM_MODEL_PATH = os.path.join(MODELS_DIR, "3ghi_lstm_model.keras")
X_SCALER_PATH = os.path.join(MODELS_DIR, "X_scaler_3LSTM.pkl")
Y_SCALER_PATH = os.path.join(MODELS_DIR, "y_scaler_3LSTM.pkl")
LGBM_GHI_PATH = os.path.join(MODELS_DIR, "Tirchy_ML_model.pkl")

# Load models and scalers
lstm_model = tf.keras.models.load_model(LSTM_MODEL_PATH, compile=False)
X_scaler = joblib.load(X_SCALER_PATH)
y_scaler = joblib.load(Y_SCALER_PATH)

lgbm_ghi_model = joblib.load(LGBM_GHI_PATH)

def fetch_weather_data(lat, lon, start_date, end_date, use_archive=False):
    """Fetch hourly weather data. use_archive=True for historical measurements, False for forecast/inference."""
    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    if use_archive:
        url = "https://archive-api.open-meteo.com/v1/archive"
    else:
        url = "https://api.open-meteo.com/v1/forecast"
    
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": [
            "temperature_2m", "relative_humidity_2m", "wind_speed_10m",
            "wind_direction_10m", "surface_pressure", "cloud_cover",
            "total_column_integrated_water_vapour", "shortwave_radiation",
            "direct_normal_irradiance", "diffuse_radiation"
        ],
        "timezone": "Asia/Kolkata"
    }
    
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    hourly = response.Hourly()
    
    timestamps = pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        periods=len(hourly.Variables(0).ValuesAsNumpy()),
        freq="h"
    ).tz_convert("Asia/Kolkata")

    df = pd.DataFrame({
        "timestamp": timestamps,
        "temperature": hourly.Variables(0).ValuesAsNumpy(),
        "humidity": hourly.Variables(1).ValuesAsNumpy(),
        "wind_speed": hourly.Variables(2).ValuesAsNumpy(),
        "wind_direction": hourly.Variables(3).ValuesAsNumpy(),
        "surface_pressure": hourly.Variables(4).ValuesAsNumpy(),
        "cloud_cover": hourly.Variables(5).ValuesAsNumpy(),
        "water_vapour": hourly.Variables(6).ValuesAsNumpy(),
        "ghi": hourly.Variables(7).ValuesAsNumpy(),
        "dni": hourly.Variables(8).ValuesAsNumpy(),
        "dhi": hourly.Variables(9).ValuesAsNumpy(),
    })
    return df

def calculate_power(df):
    df = df.copy()

    # Solar elevation
    df["solar_elevation"] = 90 - df["solar_zenith"]

    # Convert to radians
    elevation_rad = np.radians(df["solar_elevation"])
    tilt_rad = np.radians(TILT)

    # Avoid division by zero at low sun angles
    sin_elevation = np.sin(elevation_rad).clip(lower=1e-6)

    # Tilt-adjusted POA irradiance
    df["poa_irradiance"] = df["ghi_pred"] * (
        np.sin(elevation_rad + tilt_rad) / sin_elevation
    )

    # Zero irradiance if sun too low
    df.loc[df["solar_elevation"] < SUN_ELEVATION_LIMIT, "poa_irradiance"] = 0

    # Physical cap
    df["poa_irradiance"] = df["poa_irradiance"].clip(lower=0, upper=1100)

    # Cell temperature (NOCT model)
    df["cell_temperature"] = (
        df["temperature"] + (NOCT - 20) / 800 * df["poa_irradiance"]
    )

    # Temperature correction factor
    df["temp_factor"] = 1 + TEMP_COEFF * (df["cell_temperature"] - 25)

    # DC Power (MW)
    df["dc_power_mw"] = (
        df["poa_irradiance"]
        * TOTAL_PV_AREA
        * PV_EFFICIENCY
        * df["temp_factor"]
        * DERATE
    ) / 1e6

    return df["dc_power_mw"].clip(lower=0)


def predict_lstm_for_day(target_date_str):
    """Run LSTM prediction for a specific day."""
    target_dt = datetime.strptime(target_date_str, "%Y-%m-%d")
    hist_start = (target_dt - timedelta(days=2)).strftime("%Y-%m-%d")
    hist_end = (target_dt - timedelta(days=1)).strftime("%Y-%m-%d")
    
    df_hist = fetch_weather_data(LAT, LON, hist_start, hist_end)
    df_hist = add_solar_features_ist(df_hist, LAT, LON)
    df_hist = df_hist.fillna(0)
    
    X_scaled = X_scaler.transform(df_hist[FEATURES])
    X_input = X_scaled[-SEQ_LEN:].reshape(1, SEQ_LEN, len(FEATURES))
    
    y_pred_raw = lstm_model.predict(X_input).reshape(-1, 1)
    y_pred = y_scaler.inverse_transform(y_pred_raw).flatten()
    
    df_target = fetch_weather_data(LAT, LON, target_date_str, target_date_str)
    df_target = add_solar_features_ist(df_target, LAT, LON)
    df_target["ghi_pred"] = y_pred.clip(min=0)
    df_target["power"] = calculate_power(df_target)
    
    return df_target.reset_index()


def predict_lgbm_for_day(target_date_str):
    """Run LGBM prediction for a specific day."""
    df_target = fetch_weather_data(LAT, LON, target_date_str, target_date_str)
    df_target = add_solar_features_ist(df_target, LAT, LON)
    
    # GHI Prediction
    ghi_features = [
        "kt", "solar_zenith", "cos_zenith", "cloud_cover",
        "temperature", "humidity", "wind_speed", "surface_pressure",
        "clear_ghi", "wind_direction", "water_vapour",
        "dni", "dhi", "hour_sin", "hour_cos", "day_sin",
        "day_cos", "ghi_clear_weighted"
    ]
    df_target["ghi_pred"] = np.maximum(lgbm_ghi_model.predict(df_target[ghi_features]), 0)
    
    # Physical Power Calculation
    df_target["power"] = calculate_power(df_target)
    
    # Night cleanup (optional here since calculate_power does some, but consistent with notebook)
    df_target.loc[df_target["cos_zenith"] <= 0, ["ghi_pred", "power"]] = 0
    
    return df_target.reset_index()

def fetch_actual_data_for_day(date_str):
    """Fetch archival weather data and calculate actual power generation."""
    # Use fetch_weather_data with use_archive=True for ground truth
    df = fetch_weather_data(LAT, LON, date_str, date_str, use_archive=True)
    df = add_solar_features_ist(df, LAT, LON)
    
    # For actual data, 'ghi' from API is used as the 'pred' for the unified power function
    df["ghi_pred"] = df["ghi"]
    df["power"] = calculate_power(df)
    
    # Night cleanup
    df.loc[df["cos_zenith"] <= 0, ["ghi_pred", "power"]] = 0
    
    return df.reset_index()

def get_total_mwh(df_target):
    """Sum hourly MW to get total MWh for the day."""
    return df_target["power"].sum()

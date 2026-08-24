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

# Features are now loaded from models/configs

# Paths to models
APP_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(os.path.dirname(APP_DIR), "models")

LSTM_MODEL_PATH = os.path.join(MODELS_DIR, "Tirchy_LSTM_model_nolag.h5")
X_SCALER_PATH = os.path.join(MODELS_DIR, "X_scaler_lstm.pkl")
Y_SCALER_PATH = os.path.join(MODELS_DIR, "y_scaler_lstm.pkl")
LSTM_CONFIG_PATH = os.path.join(MODELS_DIR, "lstm_config.pkl")

LGBM_GHI_PATH = os.path.join(MODELS_DIR, "Tirchy_ML_model copy.pkl")
BIAS_INFO_PATH = os.path.join(MODELS_DIR, "bias_correction.pkl")
FEATURES_INFO_PATH = os.path.join(MODELS_DIR, "features.pkl")

# Load models and scalers
lstm_model = tf.keras.models.load_model(LSTM_MODEL_PATH, compile=False)
X_scaler = joblib.load(X_SCALER_PATH)
y_scaler = joblib.load(Y_SCALER_PATH)
lstm_config = joblib.load(LSTM_CONFIG_PATH)

SEQ_LEN = lstm_config['SEQ_LEN']
HORIZON = lstm_config['HORIZON']
LSTM_FEATURES = lstm_config['features']

lgbm_ghi_model = joblib.load(LGBM_GHI_PATH)
lgbm_bias_info = joblib.load(BIAS_INFO_PATH)
lgbm_features_info = joblib.load(FEATURES_INFO_PATH)
lgbm_features = lgbm_features_info['features']

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

def add_advanced_features_lgbm(df):
    """Add all engineered features for LGBM based on new model requirements."""
    df = df.copy()
    
    # Ensure hour and month are present
    if "hour" not in df.columns:
        if isinstance(df.index, pd.DatetimeIndex):
            df["hour"] = df.index.hour
        else:
            df["hour"] = df["timestamp"].dt.hour
    if "month" not in df.columns:
        if isinstance(df.index, pd.DatetimeIndex):
            df["month"] = df.index.month
        else:
            df["month"] = df["timestamp"].dt.month

    # Solar geometry
    df['ghi_potential'] = df['cos_zenith'] * 1000
    df['zenith_squared'] = df['solar_zenith'] ** 2
    df['cos_zenith_cubed'] = df['cos_zenith'] ** 3
    df['zenith_cos_interaction'] = df['solar_zenith'] * df['cos_zenith']
    
    # Cloud features
    df['cloud_impact'] = df['cloud_cover'] * df['cos_zenith']
    df['cloud_squared'] = df['cloud_cover'] ** 2
    df['cloud_cubed'] = df['cloud_cover'] ** 3
    df['cloud_inv'] = 1 / (df['cloud_cover'] + 1)
    
    # Atmospheric
    df['temp_humidity_ratio'] = df['temperature'] / (df['humidity'] + 1)
    df['water_vapour'] = 0.1 * df['humidity'] # Overwrite with engineering from snippet
    df['vapor_pressure'] = df['water_vapour'] * df['surface_pressure']
    df['temp_squared'] = df['temperature'] ** 2
    df['humidity_squared'] = df['humidity'] ** 2
    
    # Time interactions
    df['cloud_hour_interaction'] = df['cloud_cover'] * np.abs(df['hour'] - 12)
    df['temp_hour_interaction'] = df['temperature'] * np.abs(df['hour'] - 12)
    
    # Seasonal
    df['is_summer'] = ((df['month'] >= 3) & (df['month'] <= 5)).astype(int)
    df['is_monsoon'] = ((df['month'] >= 6) & (df['month'] <= 9)).astype(int)
    df['is_winter'] = ((df['month'] >= 11) | (df['month'] <= 2)).astype(int)
    
    # Rolling features
    df['cloud_roll3_mean'] = df['cloud_cover'].rolling(3, min_periods=1).mean()
    df['cloud_roll6_mean'] = df['cloud_cover'].rolling(6, min_periods=1).mean()
    df['temp_roll3_std'] = df['temperature'].rolling(3, min_periods=1).std().fillna(0)
    df['temp_roll6_mean'] = df['temperature'].rolling(6, min_periods=1).mean()
    df['humidity_roll3_mean'] = df['humidity'].rolling(3, min_periods=1).mean()
    df['wind_roll3_mean'] = df['wind_speed'].rolling(3, min_periods=1).mean()
    
    # Lag features (use defaults - no historical data provided for LGBM sequence)
    df['ghi_lag24'] = 450.0
    df['cloud_lag24'] = 50.0
    df['temp_lag24'] = df['temperature'].mean()
    
    # Clear sky index (use default)
    df['clearsky_index_roll24'] = 0.6
    df['clearsky_index_roll12'] = 0.6
    return df
# In your inference code - simplified calculate_power
def calculate_power(df):
    df = df.copy()

    df["solar_elevation"] = 90 - df["solar_zenith"]

    # Zero irradiance if sun too low
    df.loc[df["solar_elevation"] < SUN_ELEVATION_LIMIT, "poa_irradiance"] = 0

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
    """Run LSTM prediction for a specific day using 48h history."""
    target_dt = datetime.strptime(target_date_str, "%Y-%m-%d")
    start_date = (target_dt - timedelta(days=2)).strftime("%Y-%m-%d")
    end_date = target_date_str
    
    df = fetch_weather_data(LAT, LON, start_date, end_date)
    df = add_solar_features_ist(df, LAT, LON)
    df = df.fillna(0)
    
    # Feature engineering for LSTM
    df["water_vapour"] = 0.1 * df["humidity"]
    
    X_scaled = X_scaler.transform(df[LSTM_FEATURES])
    # Sequence: hours -72 to -24 (the 48 hours before target day)
    X_seq = X_scaled[-SEQ_LEN - HORIZON : -HORIZON].reshape(1, SEQ_LEN, len(LSTM_FEATURES))
    
    y_pred_scaled = lstm_model.predict(X_seq, verbose=0).reshape(-1, 1)
    y_pred = y_scaler.inverse_transform(y_pred_scaled).flatten()
    
    # Target day data (last 24 hours of fetched data)
    df_target = df.iloc[-HORIZON:].copy()
    df_target["ghi_pred"] = np.maximum(y_pred, 0)
    
    # Calculate POA irradiance using predicted GHI
    df_target = add_solar_features_ist(df_target, LAT, LON)
    
    # Calculate Physical Power
    df_target["power"] = calculate_power(df_target)
    
    # Night cleanup
    df_target.loc[df_target["cos_zenith"] <= 0, ["ghi_pred", "power"]] = 0
    
    return df_target.reset_index()


def predict_lgbm_for_day(target_date_str):
    """Run LGBM prediction for a specific day with advanced features and bias correction."""
    df_target = fetch_weather_data(LAT, LON, target_date_str, target_date_str)
    df_target = add_solar_features_ist(df_target, LAT, LON)
    
    # Add advanced features
    df_target = add_advanced_features_lgbm(df_target)
    
    # GHI Prediction
    predictions = lgbm_ghi_model.predict(df_target[lgbm_features])
    df_target["ghi_pred"] = np.maximum(predictions + lgbm_bias_info['validation_bias'], 0)
    
    # Calculate POA irradiance using predicted GHI
    df_target = add_solar_features_ist(df_target, LAT, LON)
    
    # Physical Power Calculation
    df_target["power"] = calculate_power(df_target)
    
    # Night cleanup
    df_target.loc[df_target["cos_zenith"] <= 0, ["ghi_pred", "power"]] = 0
    
    return df_target.reset_index()

def fetch_actual_data_for_day(date_str):
    """Fetch archival weather data and calculate actual power generation."""
    # Use fetch_weather_data with use_archive=True for ground truth
    df = fetch_weather_data(LAT, LON, date_str, date_str, use_archive=True)
    df = add_solar_features_ist(df, LAT, LON)
    
    # For actual data, 'ghi' from API is used as the 'pred' for the unified power function
    df["ghi_pred"] = df["ghi"]
    
    # Calculate POA irradiance using GHI
    df = add_solar_features_ist(df, LAT, LON)
    
    df["power"] = calculate_power(df)
    
    # Night cleanup
    df.loc[df["cos_zenith"] <= 0, ["ghi_pred", "power"]] = 0
    
    return df.reset_index()

def get_total_mwh(df_target):
    """Sum hourly MW to get total MWh for the day."""
    return df_target["power"].sum()

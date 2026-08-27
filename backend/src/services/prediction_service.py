import pandas as pd
from datetime import datetime, timedelta
import openmeteo_requests
import requests_cache
from retry_requests import retry
from sqlalchemy.orm import Session
import logging

from src.db.models import LSTMPrediction, LGBMPrediction, ActualData
from src.ml.features import add_solar_features_ist, add_advanced_features_lgbm, calculate_power
from src.ml.inference import predict_lstm_sequence, predict_lgbm_sequence
from src.ml import inference as ml_inference

LAT = 10.7905
LON = 78.7047

def fetch_weather_data(lat, lon, start_date, end_date, use_archive=False):
    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
    today = datetime.now().date()

    if use_archive:
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat, "longitude": lon,
            "start_date": start_date, "end_date": end_date,
            "hourly": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m",
                       "wind_direction_10m", "surface_pressure", "cloud_cover",
                       "total_column_integrated_water_vapour", "shortwave_radiation",
                       "direct_normal_irradiance", "diffuse_radiation"],
            "timezone": "Asia/Kolkata"
        }
    else:
        url = "https://api.open-meteo.com/v1/forecast"
        past_days = min(93, max(0, (today - start_dt).days))
        forecast_days = max(1, (end_dt - today).days)
        params = {
            "latitude": lat, "longitude": lon,
            "past_days": past_days,
            "forecast_days": forecast_days,
            "hourly": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m",
                       "wind_direction_10m", "surface_pressure", "cloud_cover",
                       "total_column_integrated_water_vapour", "shortwave_radiation",
                       "direct_normal_irradiance", "diffuse_radiation"],
            "timezone": "Asia/Kolkata"
        }
    
    responses = openmeteo.weather_api(url, params=params)
    hourly = responses[0].Hourly()
    
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

    mask = (df["timestamp"].dt.date >= start_dt) & (df["timestamp"].dt.date <= end_dt)
    return df[mask].reset_index(drop=True)

def predict_lstm_for_day(target_date_str: str) -> pd.DataFrame:
    target_dt = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    start_date = (target_dt - timedelta(days=2)).strftime("%Y-%m-%d")
    today = datetime.now().date()
    use_archive = target_dt < today
    
    df = fetch_weather_data(LAT, LON, start_date, target_date_str, use_archive=use_archive)
    df = add_solar_features_ist(df, LAT, LON).fillna(0)
    df["water_vapour"] = 0.1 * df["humidity"]
    
    y_pred = predict_lstm_sequence(df)
    
    df_target = df.iloc[-ml_inference.HORIZON:].copy()
    df_target["ghi_pred"] = y_pred
    df_target = add_solar_features_ist(df_target, LAT, LON)
    df_target["power"] = calculate_power(df_target)
    df_target.loc[df_target["cos_zenith"] <= 0, ["ghi_pred", "power"]] = 0
    return df_target.reset_index()

def predict_lgbm_for_day(target_date_str: str) -> pd.DataFrame:
    target_dt = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    today = datetime.now().date()
    use_archive = target_dt < today
    
    df_target = fetch_weather_data(LAT, LON, target_date_str, target_date_str, use_archive=use_archive)
    df_target = add_solar_features_ist(df_target, LAT, LON)
    df_target = add_advanced_features_lgbm(df_target)
    
    df_target["ghi_pred"] = predict_lgbm_sequence(df_target)
    df_target = add_solar_features_ist(df_target, LAT, LON)
    df_target["power"] = calculate_power(df_target)
    df_target.loc[df_target["cos_zenith"] <= 0, ["ghi_pred", "power"]] = 0
    return df_target.reset_index()

def fetch_actual_data_for_day(date_str: str) -> pd.DataFrame:
    df = fetch_weather_data(LAT, LON, date_str, date_str, use_archive=True)
    df = add_solar_features_ist(df, LAT, LON)
    df["ghi_pred"] = df["ghi"]
    df = add_solar_features_ist(df, LAT, LON)
    df["power"] = calculate_power(df)
    df.loc[df["cos_zenith"] <= 0, ["ghi_pred", "power"]] = 0
    return df.reset_index()

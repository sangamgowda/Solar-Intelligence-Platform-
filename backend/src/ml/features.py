import numpy as np
import pandas as pd
from pvlib.location import Location
from pvlib.irradiance import erbs, get_total_irradiance

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
AZIMUTH = 180

def add_solar_features_ist(df, lat, lon, altitude=0, tz="Asia/Kolkata"):
    if not isinstance(df.index, pd.DatetimeIndex):
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.set_index("timestamp")

    if df.index.tz is None:
        df.index = df.index.tz_localize(tz)
    else:
        df.index = df.index.tz_convert(tz)

    site = Location(lat, lon, altitude=altitude, tz=tz)

    solpos = site.get_solarposition(df.index)
    df["solar_zenith"] = solpos["apparent_zenith"]
    df["solar_azimuth"] = solpos["azimuth"]
    df["cos_zenith"] = np.cos(np.radians(df["solar_zenith"])).clip(lower=0)

    local_hour = df.index.hour + df.index.minute / 60
    df["hour_sin"] = np.sin(2 * np.pi * local_hour / 24)
    df["hour_cos"] = np.cos(2 * np.pi * local_hour / 24)

    df["day_sin"] = np.sin(2 * np.pi * df.index.dayofyear / 365.25)
    df["day_cos"] = np.cos(2 * np.pi * df.index.dayofyear / 365.25)
    
    clearsky = site.get_clearsky(df.index)
    df["clear_ghi"] = clearsky["ghi"]

    df["kt"] = (df["ghi"] / df["clear_ghi"]).replace([np.inf, -np.inf], 0).fillna(0)
    df["ghi_clear_weighted"] = df["clear_ghi"] * df["cos_zenith"]

    # POA calculation (only if ghi_pred exists)
    if 'ghi_pred' in df.columns:
        decomposed = erbs(
            ghi=df['ghi_pred'],
            zenith=df['solar_zenith'],
            datetime_or_doy=df.index.dayofyear
        )
        df['dni_est'] = decomposed['dni']
        df['dhi_est'] = decomposed['dhi']

        poa = get_total_irradiance(
            surface_tilt=TILT,
            surface_azimuth=AZIMUTH,
            solar_zenith=df['solar_zenith'],
            solar_azimuth=df['solar_azimuth'],
            dni=df['dni_est'],
            ghi=df['ghi_pred'],
            dhi=df['dhi_est']
        )
        df['poa_irradiance'] = poa['poa_global'].clip(lower=0, upper=1200)

    return df

def add_advanced_features_lgbm(df):
    df = df.copy()
    if "hour" not in df.columns:
        df["hour"] = df.index.hour if isinstance(df.index, pd.DatetimeIndex) else df["timestamp"].dt.hour
    if "month" not in df.columns:
        df["month"] = df.index.month if isinstance(df.index, pd.DatetimeIndex) else df["timestamp"].dt.month

    df['ghi_potential'] = df['cos_zenith'] * 1000
    df['zenith_squared'] = df['solar_zenith'] ** 2
    df['cos_zenith_cubed'] = df['cos_zenith'] ** 3
    df['zenith_cos_interaction'] = df['solar_zenith'] * df['cos_zenith']
    
    df['cloud_impact'] = df['cloud_cover'] * df['cos_zenith']
    df['cloud_squared'] = df['cloud_cover'] ** 2
    df['cloud_cubed'] = df['cloud_cover'] ** 3
    df['cloud_inv'] = 1 / (df['cloud_cover'] + 1)
    
    df['temp_humidity_ratio'] = df['temperature'] / (df['humidity'] + 1)
    df['water_vapour'] = 0.1 * df['humidity']
    df['vapor_pressure'] = df['water_vapour'] * df['surface_pressure']
    df['temp_squared'] = df['temperature'] ** 2
    df['humidity_squared'] = df['humidity'] ** 2
    
    df['cloud_hour_interaction'] = df['cloud_cover'] * np.abs(df['hour'] - 12)
    df['temp_hour_interaction'] = df['temperature'] * np.abs(df['hour'] - 12)
    
    df['is_summer'] = ((df['month'] >= 3) & (df['month'] <= 5)).astype(int)
    df['is_monsoon'] = ((df['month'] >= 6) & (df['month'] <= 9)).astype(int)
    df['is_winter'] = ((df['month'] >= 11) | (df['month'] <= 2)).astype(int)
    
    df['cloud_roll3_mean'] = df['cloud_cover'].rolling(3, min_periods=1).mean()
    df['cloud_roll6_mean'] = df['cloud_cover'].rolling(6, min_periods=1).mean()
    df['temp_roll3_std'] = df['temperature'].rolling(3, min_periods=1).std().fillna(0)
    df['temp_roll6_mean'] = df['temperature'].rolling(6, min_periods=1).mean()
    df['humidity_roll3_mean'] = df['humidity'].rolling(3, min_periods=1).mean()
    df['wind_roll3_mean'] = df['wind_speed'].rolling(3, min_periods=1).mean()
    
    df['ghi_lag24'] = 450.0
    df['cloud_lag24'] = 50.0
    df['temp_lag24'] = df['temperature'].mean()
    
    df['clearsky_index_roll24'] = 0.6
    df['clearsky_index_roll12'] = 0.6
    return df

def calculate_power(df):
    df = df.copy()
    df["solar_elevation"] = 90 - df["solar_zenith"]
    df.loc[df["solar_elevation"] < SUN_ELEVATION_LIMIT, "poa_irradiance"] = 0
    df["cell_temperature"] = df["temperature"] + (NOCT - 20) / 800 * df["poa_irradiance"]
    df["temp_factor"] = 1 + TEMP_COEFF * (df["cell_temperature"] - 25)
    df["dc_power_mw"] = (df["poa_irradiance"] * TOTAL_PV_AREA * PV_EFFICIENCY * df["temp_factor"] * DERATE) / 1e6
    return df["dc_power_mw"].clip(lower=0)

# utils.py
import numpy as np
import pandas as pd
from pvlib.location import Location
from pvlib.irradiance import erbs, get_total_irradiance

def add_solar_features_ist(df, lat, lon, altitude=0, tz="Asia/Kolkata", tilt=12, azimuth=180):
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
    df["solar_azimuth"] = solpos["azimuth"]  # Added
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

    # POA calculation (only if ghi_pred exists, otherwise skip)
    if 'ghi_pred' in df.columns:
        # Decompose GHI into DNI and DHI
        decomposed = erbs(
            ghi=df['ghi_pred'],
            zenith=df['solar_zenith'],
            datetime_or_doy=df.index.dayofyear
        )
        df['dni_est'] = decomposed['dni']
        df['dhi_est'] = decomposed['dhi']

        # Calculate POA irradiance
        poa = get_total_irradiance(
            surface_tilt=tilt,
            surface_azimuth=azimuth,
            solar_zenith=df['solar_zenith'],
            solar_azimuth=df['solar_azimuth'],
            dni=df['dni_est'],
            ghi=df['ghi_pred'],
            dhi=df['dhi_est']
        )
        df['poa_irradiance'] = poa['poa_global'].clip(lower=0, upper=1200)

    return df
from sqlalchemy import Column, Integer, Float, String, DateTime, UniqueConstraint
from .database import Base, engine, SessionLocal

class LSTMPrediction(Base):
    __tablename__ = "lstm_predictions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, unique=True, index=True, nullable=False)
    
    # Core outputs
    ghi = Column(Float)  # Predicted GHI
    power = Column(Float) # Calculated Power
    
    # Feature columns
    temperature = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(Float)
    surface_pressure = Column(Float)
    cloud_cover = Column(Float)
    water_vapour = Column(Float)
    dni = Column(Float)
    dhi = Column(Float)
    

    kt = Column(Float)
    solar_zenith = Column(Float)
    cos_zenith = Column(Float)
    clear_ghi = Column(Float)
    ghi_clear_weighted = Column(Float)
    hour_sin = Column(Float)
    hour_cos = Column(Float)
    day_sin = Column(Float)
    day_cos = Column(Float)

    __table_args__ = (UniqueConstraint('timestamp', name='_lstm_timestamp_uc'),)

class LGBMPrediction(Base):
    __tablename__ = "lgbm_predictions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, unique=True, index=True, nullable=False)
    
    # Core outputs
    ghi = Column(Float)  # Predicted GHI
    power = Column(Float) # Calculated Power
    
    # Feature columns
    temperature = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(Float)
    surface_pressure = Column(Float)
    cloud_cover = Column(Float)
    water_vapour = Column(Float)
    dni = Column(Float)
    dhi = Column(Float)
    
    # Engineered features
    kt = Column(Float)
    solar_zenith = Column(Float)
    cos_zenith = Column(Float)
    clear_ghi = Column(Float)
    ghi_clear_weighted = Column(Float)
    hour_sin = Column(Float)
    hour_cos = Column(Float)
    day_sin = Column(Float)
    day_cos = Column(Float)

    __table_args__ = (UniqueConstraint('timestamp', name='_lgbm_timestamp_uc'),)

class ActualData(Base):
    __tablename__ = "Actual_data_open_meteo"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, unique=True, index=True, nullable=False)
    
    # Core outputs
    ghi = Column(Float)  # Actual GHI from archive
    power = Column(Float) # Calculated Power using actual GHI
    
    # Feature columns
    temperature = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(Float)
    surface_pressure = Column(Float)
    cloud_cover = Column(Float)
    water_vapour = Column(Float)
    dni = Column(Float)
    dhi = Column(Float)
    
    # Engineered features
    kt = Column(Float)
    solar_zenith = Column(Float)
    cos_zenith = Column(Float)
    clear_ghi = Column(Float)
    ghi_clear_weighted = Column(Float)
    hour_sin = Column(Float)
    hour_cos = Column(Float)
    day_sin = Column(Float)
    day_cos = Column(Float)

    __table_args__ = (UniqueConstraint('timestamp', name='_actual_timestamp_uc'),)

def init_db():
    # If standard init is not enough, we can force drop in main.py
    Base.metadata.create_all(bind=engine)

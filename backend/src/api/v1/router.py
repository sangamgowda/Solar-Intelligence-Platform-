from fastapi import APIRouter

from src.api.v1.endpoints import weather, predictions, analytics

api_router = APIRouter()
api_router.include_router(weather.router, tags=["weather"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

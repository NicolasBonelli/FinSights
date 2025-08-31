"""
API router for version 1.
"""
from fastapi import APIRouter
from backend.app.api.v1.endpoints import ingestion

api_router = APIRouter()

api_router.include_router(ingestion.router, prefix="/ingest", tags=["Ingestion"])

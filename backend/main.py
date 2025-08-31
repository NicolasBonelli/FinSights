"""
FastAPI main application for FinSights - Financial Analysis System
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import get_settings
from app.core.lifespan import startup_event, shutdown_event
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    await startup_event()
    yield
    # Shutdown
    await shutdown_event()


def create_application() -> FastAPI:
    """Application factory pattern"""
    settings = get_settings()
    
    app = FastAPI(
        title="FinSights API",
        description="Financial Analysis System with Multi-Agent CrewAI",
        version="1.0.0",
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url="/redoc" if settings.environment != "production" else None,
        lifespan=lifespan
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts
    )
    

    
    # Include routers
    app.include_router(api_router, prefix="/api/v1")
    
    return app


app = create_application()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "FinSights API is running", "status": "healthy"}


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "FinSights API",
        "version": "1.0.0"
    }

from fastapi import APIRouter
from app.api.routes import analysis, health, history

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(analysis.router, prefix="/api/analyses", tags=["Document processing"])
api_router.include_router(history.router, prefix="/api/analyses", tags=["Analysis history"])

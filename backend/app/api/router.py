from fastapi import APIRouter
from app.api.endpoints import analysis, history, resource

api_router = APIRouter()

api_router.include_router(analysis.router, prefix="/analysis", tags=["分析"])
api_router.include_router(history.router, prefix="/history", tags=["历史记录"])
api_router.include_router(resource.router, prefix="/resource", tags=["资源检索"])

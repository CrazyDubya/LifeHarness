from fastapi import APIRouter
from app.api import auth, profile, threads, entries, autobiography, monitoring

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(threads.router, prefix="/threads", tags=["threads"])
api_router.include_router(entries.router, prefix="/entries", tags=["entries"])
api_router.include_router(autobiography.router, prefix="/autobiography", tags=["autobiography"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])

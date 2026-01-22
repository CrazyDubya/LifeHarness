from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.core.logging_config import setup_logging
from app.api import api_router

# Setup logging
setup_logging()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Life Harness API",
    description="Infinite autobiographical documentation system",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Life Harness API", "version": "0.1.0"}


@app.get("/health")
def health():
    return {"status": "ok"}

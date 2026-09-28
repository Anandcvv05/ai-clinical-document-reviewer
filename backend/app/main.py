from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.config import settings
from app.database.connection import init_db

app = FastAPI(
    title="AI Clinical Document Reviewer API",
    description="Backend API for processing synthetic clinical documents.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(api_router)

@app.get("/")
def root():
    return {
        "message": "AI Clinical Document Reviewer API is running",
        "docs": "/docs",
    }

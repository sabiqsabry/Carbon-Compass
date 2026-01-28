from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import analysis, compare, upload
from .models.database import close_db, init_db
from .models.schemas import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup: Initialize database
    print("🚀 Starting Carbon Compass API...")
    print("📊 Initializing database...")
    try:
        await init_db()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"⚠️  Database initialization failed: {e}")
        print("   Continuing without database (using in-memory cache)")
    
    yield
    
    # Shutdown: Close database connections
    print("🛑 Shutting down Carbon Compass API...")
    await close_db()
    print("✅ Database connections closed")


app = FastAPI(title="Carbon Compass API", lifespan=lifespan)

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"

app.include_router(upload.router, prefix=API_PREFIX)
app.include_router(analysis.router, prefix=API_PREFIX)
app.include_router(compare.router, prefix=API_PREFIX)


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", timestamp=datetime.now(timezone.utc))


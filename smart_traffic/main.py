"""
Smart Traffic Congestion Control System
========================================
A production-ready FastAPI backend that simulates a smart city traffic
control engine, predicts congestion at 9 junctions, and dynamically
allocates traffic signal timings using ML-based prediction.

Run with:
    uvicorn main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.auth import router as auth_router
from routes.simulate import router as simulate_router
from routes.admin import router as admin_router
from routes.model_info import router as model_info_router
from services.auth_service import create_default_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create default admin user on startup."""
    create_default_admin()
    yield


app = FastAPI(
    title="Smart Traffic Congestion Control System",
    description=(
        "Simulates a smart city traffic control engine that predicts "
        "congestion at 9 junctions and dynamically allocates signal timings."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS – allow the Vite dev-server frontend
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(simulate_router, prefix="/api", tags=["Simulation"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(model_info_router, prefix="/api/model", tags=["Model"])


@app.get("/", tags=["Health"])
async def root() -> dict[str, str]:
    """Health-check endpoint."""
    return {"status": "ok", "service": "Smart Traffic Congestion Control System"}

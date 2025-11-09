"""FastAPI application entry point."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ..version import __version__
from .api.routes import router
from .database import init_db

# Initialize database on startup
init_db()

app = FastAPI(
    title="XML to SQL Converter",
    description="Convert SAP HANA calculation view XML definitions into Snowflake SQL artifacts",
    version=__version__,
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes (must be before static file mount to take precedence)
app.include_router(router)

# Serve static files (React build) if they exist
# Calculate path: from src/xml_to_sql/web/main.py -> project root -> web_frontend/dist
_project_root = Path(__file__).parent.parent.parent.parent
frontend_build_path = _project_root / "web_frontend" / "dist"

if frontend_build_path.exists() and (frontend_build_path / "index.html").exists():
    # Mount static files - this will serve index.html for "/" and other static assets
    # API routes under "/api" will still work because they're more specific
    app.mount("/", StaticFiles(directory=str(frontend_build_path), html=True), name="static")
else:
    # Fallback: serve a simple message if frontend not built
    @app.get("/")
    async def root():
        return {
            "message": "XML to SQL Converter API",
            "docs": "/docs",
            "note": f"Frontend not built. Expected at: {frontend_build_path}. Run 'npm run build' in web_frontend directory.",
        }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/api/version")
async def get_version():
    """Get application version."""
    return {"version": __version__}


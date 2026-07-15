from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# ── CORS ───────────────────────────────────────────────────────────────────────
# Origins are read from the ALLOWED_ORIGINS env var (comma-separated string)
# so they can be different between local dev and production without code changes.
# Dev default (set in config.py): localhost:3000 and localhost:5173
# Production: set ALLOWED_ORIGINS=https://fit.alphazero.dev in the Render dashboard
origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ─────────────────────────────────────────────────────────────────────
# Mount all routes under /api/v1
# Versioning from day one costs nothing and saves a lot of pain later
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": f"Welcome to the {settings.PROJECT_NAME}. Docs at /docs"}
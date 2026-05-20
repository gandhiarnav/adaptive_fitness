from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# ── CORS ───────────────────────────────────────────────────────────────────────
# Allow the frontend dev server to talk to this API.
# Add any other origins (staging URLs, etc.) to this list as needed.
origins = [
    "http://localhost:3000",   # React / Create-React-App default
    "http://localhost:5173",   # Vite / Vue default
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "https://mechanism-points-varies-prot.trycloudflare.com",  # Cloudflare tunnel
]

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
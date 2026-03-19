from fastapi import FastAPI
 
from app.api.router import api_router
from app.core.config import settings
 
app = FastAPI(title=settings.PROJECT_NAME)
 
# Mount all routes under /api/v1
# Versioning from day one costs nothing and saves a lot of pain later
app.include_router(api_router, prefix="/api/v1")
 
 
@app.get("/")
def read_root():
    return {"message": f"Welcome to the {settings.PROJECT_NAME}. Docs at /docs"}
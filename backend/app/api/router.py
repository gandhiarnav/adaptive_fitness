from fastapi import APIRouter

from app.api.routes import auth, users, profile, food_journal, workout, summary, admin, saved_meals

# This is the single router that main.py imports.
# Adding a new feature in future = add one line here.
api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(profile.router)
api_router.include_router(food_journal.router)
api_router.include_router(workout.router)
api_router.include_router(summary.router)
api_router.include_router(admin.router)
api_router.include_router(saved_meals.router)

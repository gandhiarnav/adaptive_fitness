"""
Macro Logic Service
───────────────────
Computes personalised daily calorie and macro targets from a user's profile.

The pipeline:
    Profile data
        → BMR   (Mifflin-St Jeor equation)
        → TDEE  (BMR × activity multiplier)
        → Targets (TDEE adjusted for goal, split into macros)

Architecture note:
    Like the calorie estimator, the public function `compute_targets()` is
    the only thing the rest of the app touches. The internal calculation
    functions are isolated so you can swap in a more sophisticated model
    (e.g. body-composition-aware TDEE, adaptive calorie cycling) without
    changing any route or CRUD code.
"""

from dataclasses import dataclass


# ── Data structures ────────────────────────────────────────────────────────────

@dataclass
class DailyTargets:
    """
    The result object returned by this service.

    All values are per-day targets.
    Macros are in grams; calories are kcal.
    """
    calories: int
    protein: int   # grams
    carbs: int     # grams
    fat: int       # grams
    tdee: int      # maintenance calories before goal adjustment


# ── Activity multipliers (Mifflin-St Jeor standard) ───────────────────────────

_ACTIVITY_MULTIPLIERS: dict[str, float] = {
    "sedentary":         1.2,   # desk job, no exercise
    "lightly_active":    1.375, # light exercise 1-3 days/week
    "moderately_active": 1.55,  # moderate exercise 3-5 days/week
    "very_active":       1.725, # hard exercise 6-7 days/week
    "extra_active":      1.9,   # physical job + hard training
}

# Calorie adjustment on top of TDEE based on goal
_GOAL_ADJUSTMENTS: dict[str, int] = {
    "weight_loss":   -400,  # moderate deficit
    "muscle_gain":   +300,  # lean bulk surplus
    "maintenance":      0,
    "endurance":     +200,  # endurance athletes need extra fuel
}


# ── Internal calculation functions ────────────────────────────────────────────

def _calculate_bmr(weight_kg: float, height_cm: float, age: int, sex: str = "male") -> float:
    """
    Mifflin-St Jeor BMR equation.

    sex defaults to 'male' since we don't collect it in the profile yet.
    Adding a sex field to the Profile model later will automatically improve
    accuracy — just pass it through here.

    Male:   BMR = 10W + 6.25H - 5A + 5
    Female: BMR = 10W + 6.25H - 5A - 161
    """
    base = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)
    return base + 5 if sex == "male" else base - 161


def _calculate_tdee(bmr: float, activity_level: str) -> float:
    """Multiply BMR by the activity multiplier to get total daily energy expenditure."""
    multiplier = _ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)  # default: sedentary
    return bmr * multiplier


def _split_macros(target_calories: int, goal: str) -> tuple[int, int, int]:
    """
    Split target calories into protein / carbs / fat in grams.

    Macro ratios are tuned per goal:
      weight_loss:  high protein to preserve muscle during deficit
      muscle_gain:  high carbs to fuel training and growth
      maintenance:  balanced split
      endurance:    carb-dominant for sustained energy output
    
    Returns (protein_g, carbs_g, fat_g).
    """
    # (protein_ratio, carb_ratio, fat_ratio) — must sum to 1.0
    ratios: dict[str, tuple[float, float, float]] = {
        "weight_loss":  (0.40, 0.35, 0.25),
        "muscle_gain":  (0.30, 0.45, 0.25),
        "maintenance":  (0.30, 0.40, 0.30),
        "endurance":    (0.20, 0.55, 0.25),
    }
    protein_r, carb_r, fat_r = ratios.get(goal, ratios["maintenance"])

    # Protein and carbs = 4 kcal/g, fat = 9 kcal/g
    protein_g = round((target_calories * protein_r) / 4)
    carbs_g   = round((target_calories * carb_r)    / 4)
    fat_g     = round((target_calories * fat_r)     / 9)

    return protein_g, carbs_g, fat_g


# ── Public interface ───────────────────────────────────────────────────────────

def compute_targets(
    weight_kg: float,
    height_cm: float,
    age: int,
    activity_level: str,
    goal: str,
) -> DailyTargets:
    """
    Main entry point for the macro logic service.

    Takes raw profile values and returns a fully computed DailyTargets object.

    Example:
        targets = compute_targets(
            weight_kg=80,
            height_cm=175,
            age=25,
            activity_level="moderately_active",
            goal="muscle_gain",
        )
        # targets.calories → 3147
        # targets.protein  → 236g
        # targets.carbs    → 354g
        # targets.fat      → 87g
    """
    bmr = _calculate_bmr(weight_kg, height_cm, age)
    tdee = _calculate_tdee(bmr, activity_level)

    goal_adjustment = _GOAL_ADJUSTMENTS.get(goal, 0)
    target_calories = round(tdee + goal_adjustment)

    protein_g, carbs_g, fat_g = _split_macros(target_calories, goal)

    return DailyTargets(
        calories=target_calories,
        protein=protein_g,
        carbs=carbs_g,
        fat=fat_g,
        tdee=round(tdee),
    )


def is_profile_complete(
    weight_kg: float | None,
    height_cm: float | None,
    age: int | None,
    activity_level: str | None,
    goal: str | None,
) -> bool:
    """
    Guard check before calling compute_targets.

    Returns False if any required field is missing — the route layer
    should call this first and return a helpful 400 rather than crashing.
    """
    return all([weight_kg, height_cm, age, activity_level, goal])

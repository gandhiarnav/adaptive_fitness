"""
Calorie Estimator Service
─────────────────────────
Analyses a raw food text entry and returns estimated calories and protein.

Architecture note:
    This module is intentionally structured in two layers:

    1. `_parse_food_text()`  — the "brain". Right now it uses a keyword
       lookup table. In the future, replace ONLY this function with an ML
       model, an LLM call, or a nutrition API. Nothing outside this file
       needs to change.

    2. `estimate_macros()`   — the public interface that the route layer
       calls. It orchestrates parsing and aggregation, and is the function
       that was left as a seam in the food journal route.
"""

from dataclasses import dataclass


# ── Data structures ────────────────────────────────────────────────────────────

@dataclass
class MacroEstimate:
    """The result object returned by this service."""
    calories: int
    protein: int  # grams


@dataclass
class _FoodItem:
    """Internal: a single recognised food with its per-unit nutrition."""
    name: str
    calories_per_unit: int
    protein_per_unit: int  # grams


# ── Nutrition knowledge base ───────────────────────────────────────────────────
# Each entry represents one common unit (1 egg, 1 cup of rice, etc.)
# Expand this freely — or replace _parse_food_text() with an API/ML call.

_FOOD_DB: dict[str, _FoodItem] = {
    # Proteins
    "egg":          _FoodItem("egg",          78,   6),
    "eggs":         _FoodItem("egg",          78,   6),
    "chicken":      _FoodItem("chicken",     165,  31),
    "tuna":         _FoodItem("tuna",        130,  28),
    "salmon":       _FoodItem("salmon",      208,  20),
    "beef":         _FoodItem("beef",        250,  26),
    "paneer":       _FoodItem("paneer",      265,  18),
    "tofu":         _FoodItem("tofu",         76,   8),
    "dal":          _FoodItem("dal",         116,   9),
    "lentils":      _FoodItem("lentils",     116,   9),
    "whey":         _FoodItem("whey",        120,  25),
    # Carbs
    "rice":         _FoodItem("rice",        200,   4),
    "roti":         _FoodItem("roti",        120,   3),
    "chapati":      _FoodItem("chapati",     120,   3),
    "bread":        _FoodItem("bread",        80,   3),
    "oats":         _FoodItem("oats",        150,   5),
    "pasta":        _FoodItem("pasta",       220,   8),
    "potato":       _FoodItem("potato",      130,   3),
    "banana":       _FoodItem("banana",       89,   1),
    "apple":        _FoodItem("apple",        95,   0),
    "mango":        _FoodItem("mango",       201,   3),
    # Dairy & fats
    "milk":         _FoodItem("milk",        149,   8),
    "curd":         _FoodItem("curd",        100,  11),
    "yogurt":       _FoodItem("yogurt",      100,  11),
    "butter":       _FoodItem("butter",      102,   0),
    "cheese":       _FoodItem("cheese",      113,   7),
    # Snacks / misc
    "almonds":      _FoodItem("almonds",     164,   6),
    "peanuts":      _FoodItem("peanuts",     166,   7),
    "protein bar":  _FoodItem("protein bar", 200,  20),
}

# Quantity words and their multipliers (e.g. "two eggs" → 2)
_QUANTITY_WORDS: dict[str, int] = {
    "a": 1, "an": 1, "one": 1, "two": 2, "three": 3,
    "four": 4, "five": 5, "six": 6,
}


# ── Internal parsing layer (swap this out for ML/API later) ───────────────────

def _parse_food_text(text: str) -> list[tuple[_FoodItem, int]]:
    """
    Scan the text for known food keywords and infer quantities.

    Returns a list of (FoodItem, quantity) tuples.

    This is intentionally simple — a keyword scan with basic quantity
    detection. Replace the body of this function with any smarter logic
    (spaCy NER, GPT function-calling, Nutritionix API, etc.) and the
    rest of the service layer stays identical.
    """
    text_lower = text.lower()
    results: list[tuple[_FoodItem, int]] = []

    # Check multi-word keys first (e.g. "protein bar") before single words
    for food_key, food_item in sorted(_FOOD_DB.items(), key=lambda x: -len(x[0])):
        if food_key in text_lower:
            # Look for a numeric digit or quantity word immediately before this food
            food_index = text_lower.find(food_key)
            preceding = text_lower[:food_index].strip().split()

            quantity = 1  # default to 1 serving
            if preceding:
                last_word = preceding[-1]
                if last_word.isdigit():
                    quantity = int(last_word)
                elif last_word in _QUANTITY_WORDS:
                    quantity = _QUANTITY_WORDS[last_word]

            results.append((food_item, quantity))

            # Remove matched text to avoid double-counting substrings
            text_lower = text_lower.replace(food_key, "", 1)

    return results


# ── Public interface ───────────────────────────────────────────────────────────

def estimate_macros(raw_text: str) -> MacroEstimate:
    """
    Main entry point for the calorie estimator.

    Takes the user's raw journal text (e.g. "ate 2 eggs and a banana")
    and returns a MacroEstimate with total calories and protein.

    Returns MacroEstimate(0, 0) if no known foods are found rather than
    raising — the route layer will still save the entry, just without estimates.
    """
    parsed = _parse_food_text(raw_text)

    if not parsed:
        return MacroEstimate(calories=0, protein=0)

    total_calories = sum(item.calories_per_unit * qty for item, qty in parsed)
    total_protein = sum(item.protein_per_unit * qty for item, qty in parsed)

    return MacroEstimate(calories=total_calories, protein=total_protein)

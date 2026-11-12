"""
Calorie Estimator Service
─────────────────────────
Analyses a raw food text entry and returns estimated calories and protein.

PRIMARY PATH — Gemini AI
─────────────────────────
When GEMINI_API_KEY is set in the environment, the service sends the user's
raw food text to gemini-2.0-flash and asks it to return a strict JSON object:

    {"calories": <int>, "protein": <int>}

This handles any food description — Indian dishes, brand names, mixed meals,
informal language — far more accurately than the keyword matcher.

FALLBACK PATH — Keyword Parser
────────────────────────────────
If the Gemini API key is absent, the quota is exhausted, the model returns
unexpected output, or any other error occurs, the service silently falls back
to the built-in keyword-based estimator so the app never crashes.

HOW THE KEYWORD PARSER WORKS (fallback)
────────────────────────────────────────
Input: "had 2 rotis with a tablespoon of butter and 3 eggs"

Step 1 — Lowercase & normalise
    → "had 2 rotis with a tablespoon of butter and 3 eggs"

Step 2 — Measurement detection
    The parser scans for measurement words (tablespoon, teaspoon, cup, etc.)
    and notes their position. When a food is found after a measurement word,
    the measurement's gram-weight overrides the default serving size.

    "a tablespoon of butter"
        → measurement: tablespoon = 14g
        → food: butter = 717 kcal per 100g
        → calories = 717 * (14/100) ≈ 100 kcal  (not a full serving)

Step 3 — Food keyword scan (longest key first)
    Keys are sorted by length descending so "protein bar" is checked before
    "bar", preventing partial-match false positives.

Step 4 — Quantity detection
    For each food found, the parser looks at the word immediately before it:
        "3 eggs"     → digit   "3" → quantity = 3
        "two rotis"  → word    "two" → quantity = 2
        "a banana"   → article "a"  → quantity = 1
        "eggs"       → nothing → quantity = 1 (default)

Step 5 — Calorie & protein calculation
    Each food stores nutrition per 100g internally.
    A default_serving_g field defines what "1 unit" means (1 egg = 50g).

    calories = (calories_per_100g / 100) * grams * quantity
    protein  = (protein_per_100g  / 100) * grams * quantity

Step 6 — Aggregate and return
    All matched items are summed into a single MacroEstimate.
"""

import json
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# ── Data structures ────────────────────────────────────────────────────────────

@dataclass
class MacroEstimate:
    """The result object returned by this service."""
    calories: int
    protein: int  # grams


@dataclass
class _FoodItem:
    """
    Internal: a single food with per-100g nutrition and a default serving size.

    calories_per_100g / protein_per_100g: standard nutritional values
    default_serving_g: what "1 unit" weighs in grams
        e.g. 1 egg = 50g, 1 roti = 40g, 1 cup of rice = 195g
    """
    name: str
    calories_per_100g: float
    protein_per_100g: float
    default_serving_g: float

    @property
    def calories_per_unit(self) -> float:
        return self.calories_per_100g * self.default_serving_g / 100

    @property
    def protein_per_unit(self) -> float:
        return self.protein_per_100g * self.default_serving_g / 100


# ── Measurement units → grams ──────────────────────────────────────────────────
# When a measurement word is found before a food, these gram values replace
# the food's default_serving_g for that specific mention.

_MEASUREMENT_GRAMS: dict[str, float] = {
    # Spoon measurements
    "teaspoon":     5.0,
    "teaspoons":    5.0,
    "tsp":          5.0,
    "tablespoon":  14.0,
    "tablespoons": 14.0,
    "tbsp":        14.0,

    # Volume measurements
    "cup":        240.0,
    "cups":       240.0,
    "glass":      240.0,
    "bowl":       300.0,   # approximate medium bowl

    # Portion words
    "slice":       30.0,   # approx 1 slice of bread/paratha
    "slices":      30.0,
    "handful":     30.0,
    "piece":       80.0,
    "pieces":      80.0,
    "scoop":       30.0,   # protein powder scoop
    "scoops":      30.0,
}

# Quantity words → numeric multiplier
_QUANTITY_WORDS: dict[str, float] = {
    "a": 1, "an": 1, "one": 1, "two": 2, "three": 3,
    "four": 4, "five": 5, "six": 6, "half": 0.5,
}


# ── Nutrition knowledge base ───────────────────────────────────────────────────
# Format: "key": _FoodItem(name, kcal_per_100g, protein_per_100g, default_serving_g)

_FOOD_DB: dict[str, _FoodItem] = {

    # ── Eggs & Proteins ────────────────────────────────────────────────────────
    "egg":              _FoodItem("egg",              143, 13.0,  50),   # 1 medium egg
    "eggs":             _FoodItem("egg",              143, 13.0,  50),
    "chicken breast":   _FoodItem("chicken breast",   165, 31.0, 150),   # 1 breast
    "chicken":          _FoodItem("chicken",          239, 27.0, 150),
    "tuna":             _FoodItem("tuna",             130, 28.0, 100),
    "salmon":           _FoodItem("salmon",           208, 20.0, 150),
    "beef":             _FoodItem("beef",             250, 26.0, 100),
    "paneer":           _FoodItem("paneer",           265, 18.0, 100),
    "tofu":             _FoodItem("tofu",              76,  8.0, 100),
    "dal":              _FoodItem("dal",               93,  5.0, 250),   # 1 bowl cooked
    "lentils":          _FoodItem("lentils",          116,  9.0, 200),
    "rajma":            _FoodItem("rajma",            127,  9.0, 250),   # 1 bowl
    "chhole":           _FoodItem("chhole",           164,  9.0, 250),
    "chickpeas":        _FoodItem("chickpeas",        164,  9.0, 200),
    "whey":             _FoodItem("whey protein",     370, 80.0,  30),   # 1 scoop
    "protein powder":   _FoodItem("protein powder",  370, 80.0,  30),

    # ── Indian Breads ──────────────────────────────────────────────────────────
    "paratha":          _FoodItem("paratha",          260,  5.5,  80),   # 1 medium paratha
    "aloo paratha":     _FoodItem("aloo paratha",     290,  6.0, 100),   # stuffed
    "roti":             _FoodItem("roti",             264,  8.9,  40),   # 1 roti
    "rotis":            _FoodItem("roti",             264,  8.9,  40),
    "chapati":          _FoodItem("chapati",          264,  8.9,  40),
    "puri":             _FoodItem("puri",             330,  6.0,  35),   # 1 small puri
    "naan":             _FoodItem("naan",             310,  9.0,  90),   # 1 naan
    "bread":            _FoodItem("bread",            265,  9.0,  30),   # 1 slice

    # ── Rice & Grains ──────────────────────────────────────────────────────────
    "rice":             _FoodItem("rice",             130,  2.7, 195),   # 1 cup cooked
    "biryani":          _FoodItem("biryani",          190,  8.0, 300),   # 1 plate
    "khichdi":          _FoodItem("khichdi",          130,  5.0, 250),
    "poha":             _FoodItem("poha",             180,  3.0, 180),   # 1 serving
    "upma":             _FoodItem("upma",             160,  4.0, 200),
    "idli":             _FoodItem("idli",              58,  2.0,  40),   # 1 idli
    "dosa":             _FoodItem("dosa",             168,  4.0, 100),   # 1 plain dosa
    "oats":             _FoodItem("oats",             379, 13.0,  40),   # 1 serving dry
    "pasta":            _FoodItem("pasta",            131,  5.0, 180),   # 1 cup cooked

    # ── Vegetables & Sides ────────────────────────────────────────────────────
    "potato":           _FoodItem("potato",            77,  2.0, 150),   # 1 medium
    "aloo":             _FoodItem("aloo",              77,  2.0, 150),
    "palak":            _FoodItem("palak",             23,  2.9, 100),
    "sabzi":            _FoodItem("sabzi",             80,  2.0, 150),   # generic veggie dish
    "sambar":           _FoodItem("sambar",            50,  3.0, 200),   # 1 bowl

    # ── Fruits ────────────────────────────────────────────────────────────────
    "banana":           _FoodItem("banana",            89,  1.1, 120),   # 1 medium
    "apple":            _FoodItem("apple",             52,  0.3, 182),   # 1 medium
    "mango":            _FoodItem("mango",             60,  0.8, 336),   # 1 whole
    "orange":           _FoodItem("orange",            47,  0.9, 180),

    # ── Dairy & Fats ──────────────────────────────────────────────────────────
    "milk":             _FoodItem("milk",              61,  3.2, 240),   # 1 glass
    "curd":             _FoodItem("curd",              98, 11.0, 200),   # 1 bowl
    "yogurt":           _FoodItem("yogurt",            59,  3.5, 200),
    "butter":           _FoodItem("butter",           717,  0.9,  10),   # base = 1 tsp (10g)
    "ghee":             _FoodItem("ghee",             900,  0.0,  10),   # base = 1 tsp
    "cheese":           _FoodItem("cheese",           402, 25.0,  28),   # 1 slice/oz
    "paneer":           _FoodItem("paneer",           265, 18.0, 100),

    # ── Oils (almost always used in tsp/tbsp, not whole units) ────────────────
    "oil":              _FoodItem("oil",              884,  0.0,  14),   # base = 1 tbsp
    "olive oil":        _FoodItem("olive oil",        884,  0.0,  14),
    "coconut oil":      _FoodItem("coconut oil",      862,  0.0,  14),

    # ── Nuts & Snacks ─────────────────────────────────────────────────────────
    "almonds":          _FoodItem("almonds",          579, 21.0,  28),   # small handful
    "peanuts":          _FoodItem("peanuts",          567, 26.0,  28),
    "peanut butter":    _FoodItem("peanut butter",    588, 25.0,  32),   # 2 tbsp
    "protein bar":      _FoodItem("protein bar",      380, 20.0,  60),   # 1 bar

    # ── Drinks ────────────────────────────────────────────────────────────────
    "chai":             _FoodItem("chai",              50,  2.0, 200),   # 1 cup with milk
    "coffee":           _FoodItem("coffee",            37,  0.6, 240),   # 1 cup with milk
    "lassi":            _FoodItem("lassi",             98,  3.0, 300),   # 1 glass sweet
}


# ── Internal parsing layer (keyword fallback) ──────────────────────────────────

def _find_measurement(words_before: list[str]) -> float | None:
    """
    Scan the words preceding a food keyword for a measurement unit.

    Returns the gram value of the measurement if found, None otherwise.

    Example: ["had", "a", "tablespoon", "of"] → 14.0 (tablespoon grams)
    """
    for word in reversed(words_before):  # scan right-to-left (closest word first)
        if word in _MEASUREMENT_GRAMS:
            return _MEASUREMENT_GRAMS[word]
    return None


def _find_quantity(words_before: list[str]) -> float:
    """
    Scan the words preceding a food keyword for a numeric quantity.

    Returns the quantity as a float (default 1.0).

    Example: ["ate", "3"] → 3.0
    Example: ["had", "two"] → 2.0
    Example: ["a", "tablespoon", "of"] → 1.0 (no standalone quantity)
    """
    for word in reversed(words_before):
        if word.replace(".", "", 1).isdigit():   # handles "2" and "2.5"
            return float(word)
        if word in _QUANTITY_WORDS:
            return float(_QUANTITY_WORDS[word])
    return 1.0


def _parse_food_text(text: str) -> list[tuple[_FoodItem, float, float]]:
    """
    Scan the text for known food keywords and infer quantities and measurements.

    Returns a list of (FoodItem, quantity, grams_per_unit) tuples.

    grams_per_unit is:
      - the measurement's gram value if a measurement word was found
        (e.g. "tablespoon of butter" → 14g, ignoring butter's default)
      - the food's default_serving_g otherwise
    """
    text_lower = text.lower()
    # Normalise common abbreviations before scanning
    text_lower = (text_lower
                  .replace("tsp", "teaspoon")
                  .replace("tbsp", "tablespoon")
                  .replace(",", " ")
                  .replace(".", " "))

    results: list[tuple[_FoodItem, float, float]] = []

    # Sort longest key first to catch multi-word items before their substrings
    for food_key, food_item in sorted(_FOOD_DB.items(), key=lambda x: -len(x[0])):
        if food_key not in text_lower:
            continue

        food_index = text_lower.find(food_key)
        words_before = text_lower[:food_index].strip().split()

        measurement_g = _find_measurement(words_before)
        quantity = _find_quantity(words_before)

        # Use measurement grams if found, otherwise food's default serving
        grams = measurement_g if measurement_g is not None else food_item.default_serving_g

        results.append((food_item, quantity, grams))

        # Erase matched text to prevent double-counting substrings
        text_lower = text_lower.replace(food_key, " ", 1)

    return results


def _keyword_estimate(raw_text: str) -> MacroEstimate:
    """Run the built-in keyword-based estimator and return a MacroEstimate."""
    parsed = _parse_food_text(raw_text)

    if not parsed:
        return MacroEstimate(calories=0, protein=0)

    total_calories = sum(
        round(item.calories_per_100g * grams / 100 * qty)
        for item, qty, grams in parsed
    )
    total_protein = sum(
        round(item.protein_per_100g * grams / 100 * qty)
        for item, qty, grams in parsed
    )

    return MacroEstimate(calories=total_calories, protein=total_protein)


# ── Gemini AI estimator ────────────────────────────────────────────────────────

_GEMINI_SYSTEM_PROMPT = """You are a nutrition expert AI assistant.

Given a food description (which may be informal, in any language, or include
Indian dish names), return ONLY a valid JSON object with the total estimated
calories and protein for everything described.

Rules:
- Return ONLY this JSON format, nothing else: {"calories": <integer>, "protein": <integer>}
- "calories" is total kilocalories (kcal) for the entire meal described
- "protein" is total grams of protein for the entire meal described
- Round both values to the nearest whole number
- If you cannot parse the input, return {"calories": 0, "protein": 0}
- Do NOT include markdown, explanation, or any text outside the JSON object
"""


_GEMINI_MODELS = (
    "gemini-3.5-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-3.1-flash-lite",
    "gemma-4-26b-a4b-it",
)


def _gemini_estimate(raw_text: str, api_key: str) -> MacroEstimate:
    """
    Call the Gemini REST API to estimate calories and protein from free text.

    Raises any exception on failure — the caller handles fallback.
    """
    import urllib.request

    prompt = f"{_GEMINI_SYSTEM_PROMPT}\n\nFood description: {raw_text}"
    payload = json.dumps({
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]},
        ],
    }).encode("utf-8")

    last_err: Exception | None = None
    response_text = ""

    for model_name in _GEMINI_MODELS:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model_name}:generateContent?key={api_key}"
        )
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                response_text = (
                    body["candidates"][0]["content"]["parts"][0]["text"].strip()
                )
                break
        except Exception as exc:
            last_err = exc
            continue
    else:
        if last_err is not None:
            raise last_err
        raise RuntimeError("No Gemini models configured")

    # Strip markdown code fences if the model wraps output despite instructions
    if response_text.startswith("```"):
        lines = response_text.splitlines()
        # Remove first and last fence lines
        inner = [l for l in lines if not l.startswith("```")]
        response_text = "\n".join(inner).strip()

    data = json.loads(response_text)

    calories = int(data.get("calories", 0))
    protein  = int(data.get("protein", 0))

    return MacroEstimate(calories=calories, protein=protein)


# ── Public interface ───────────────────────────────────────────────────────────

def estimate_macros(raw_text: str) -> MacroEstimate:
    """
    Main entry point for the calorie estimator.

    Takes the user's raw journal text and returns a MacroEstimate.

    Tries Gemini AI first (if GEMINI_API_KEY is configured). Falls back to the
    built-in keyword parser if Gemini is unavailable or returns an error.

    Returns MacroEstimate(0, 0) if neither method can detect any food.

    Examples:
        "2 eggs and a banana"
            → Gemini: ~250 kcal, 14g protein

        "a tablespoon of ghee on 2 rotis"
            → Gemini: ~337 kcal, 7g protein
    """
    # Lazy import so startup doesn't fail if the package isn't installed yet
    try:
        from app.core.config import settings
        api_key = settings.GEMINI_API_KEY
    except Exception:
        api_key = ""

    if api_key:
        try:
            result = _gemini_estimate(raw_text, api_key)
            logger.debug(
                "Gemini estimate for %r → %d kcal, %dg protein",
                raw_text[:60], result.calories, result.protein,
            )
            return result
        except Exception as exc:
            # Log the failure but don't crash — fall through to keyword parser
            logger.warning(
                "Gemini estimation failed (%s: %s). Using keyword fallback.",
                type(exc).__name__, exc,
            )

    # Keyword-based fallback
    return _keyword_estimate(raw_text)

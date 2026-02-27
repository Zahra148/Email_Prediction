# packages/shared/uma_shared/engines.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import math

_ZONE_TABLE: list[tuple[float, float, str]] = [
    (50.0,  90.0, "3a"),   # Northern Canada, Alaska
    (47.0,  50.0, "4a"),   # Northern US border states
    (45.0,  47.0, "5a"),   # Minnesota, Wisconsin, Vermont
    (42.0,  45.0, "6a"),   # Ohio, Pennsylvania, Colorado
    (39.0,  42.0, "7a"),   # Virginia, Kansas, Oregon coast
    (36.0,  39.0, "8a"),   # North Carolina, Tennessee, Pacific NW
    (33.0,  36.0, "9a"),   # Georgia, Alabama, Northern California
    (30.0,  33.0, "9b"),   # South Carolina, Central California
    (27.0,  30.0, "10a"),  # South Florida, Southern California
    (24.0,  27.0, "10b"),  # Miami, Hawaii
    (0.0,   24.0, "11a"),  # Tropical regions
]


def _get_usda_zone(lat: float) -> str:
    """
    Returns the USDA hardiness zone for a given latitude.
    Uses absolute value so Southern hemisphere works too.

    Example:
        _get_usda_zone(37.7)  → "8a"   (San Francisco)
        _get_usda_zone(25.8)  → "10b"  (Miami)
    """
    abs_lat = abs(lat)
    for min_lat, max_lat, zone in _ZONE_TABLE:
        if min_lat <= abs_lat < max_lat:
            return zone
    return "11a"  # default for anything below 0 lat (equatorial)


def _calculate_sun_hours(lat: float, month: int) -> float:
    """
    Estimates daily usable sun hours for a given location and month.

    Args:
        lat:   Latitude in decimal degrees (-90 to 90)
        month: Month as integer (1=January, 12=December)

    Returns:
        Estimated hours of usable sunlight per day (float)

    Example:
        _calculate_sun_hours(37.7, 6)  → ~9.8 hrs  (San Francisco, June)
        _calculate_sun_hours(37.7, 12) → ~5.2 hrs  (San Francisco, December)
    """
    _MONTH_DAY = [15, 45, 74, 105, 135, 166, 196, 227, 258, 288, 319, 349]
    day_of_year = _MONTH_DAY[month - 1]

    declination = 23.45 * math.sin(math.radians((360 / 365) * (day_of_year - 81)))

    lat_rad = math.radians(lat)
    dec_rad = math.radians(declination)

    cos_hour_angle = -math.tan(lat_rad) * math.tan(dec_rad)

    cos_hour_angle = max(-1.0, min(1.0, cos_hour_angle))

    hour_angle = math.degrees(math.acos(cos_hour_angle))

    day_length = (2 * hour_angle) / 15

    # Usable sun = ~75% of day length (accounting for clouds, morning/evening low angle)
    usable_sun = round(day_length * 0.75, 1)

    return usable_sun

_SHADE_MODIFIERS: dict[str, float] = {
    "none":     1.0,   # No shade — full sun
    "partial":  0.75,  # Some shade from trees or nearby structures
    "heavy":    0.50,  # Significant shade — building or dense trees
}


@dataclass
class GardenState:
    """
    The complete environmental profile of a user's garden.
    Output of the Constraint Engine (T005).
    Read by: Planning Engine (T006), Yield Band Logic (T008).

    Fields:
        lat, lon        — garden coordinates
        usda_zone       — e.g. "9b"
        raw_sun_hours   — sun before shade adjustment
        shade_level     — "none", "partial", or "heavy"
        adjusted_sun    — sun after shade adjustment (used for crop filtering)
        month           — month the calculation was run (affects sun hours)
        garden_area_m2  — total plantable area in square meters
    """
    lat:            float
    lon:            float
    usda_zone:      str
    raw_sun_hours:  float
    shade_level:    str
    adjusted_sun:   float
    month:          int
    garden_area_m2: float

def compute_garden_state(
    lat:            float,
    lon:            float,
    month:          int,
    shade_level:    str = "none",
    garden_area_m2: float = 10.0,
) -> GardenState:

       zone = _get_usda_zone(lat)

    
    raw_sun = _calculate_sun_hours(lat, month)

        modifier = _SHADE_MODIFIERS.get(shade_level, 1.0)
    adjusted_sun = round(raw_sun * modifier, 1)

    return GardenState(
        lat            = lat,
        lon            = lon,
        usda_zone      = zone,
        raw_sun_hours  = raw_sun,
        shade_level    = shade_level,
        adjusted_sun   = adjusted_sun,
        month          = month,
        garden_area_m2 = garden_area_m2,
    )

_CROP_DB: list[dict] = [
    {
        "crop_id":       "kale",
        "crop_name":     "Kale",
        "usda_zones":    ["5a","5b","6a","6b","7a","7b","8a","8b","9a","9b","10a","10b"],
        "min_sun":       4.0,
        "optimal_sun":   6.0,
        "nutrient_tags": ["vitamin_k", "vitamin_c", "fiber"],
        "spacing_m2":    0.3,
        "base_yield_kg": 0.8,
    },
    {
        "crop_id":       "spinach",
        "crop_name":     "Spinach",
        "usda_zones":    ["4a","4b","5a","5b","6a","6b","7a","7b","8a","8b","9a","9b"],
        "min_sun":       3.0,
        "optimal_sun":   5.0,
        "nutrient_tags": ["folate", "magnesium", "vitamin_k", "fiber"],
        "spacing_m2":    0.2,
        "base_yield_kg": 0.5,
    },
    {
        "crop_id":       "garlic",
        "crop_name":     "Garlic",
        "usda_zones":    ["4a","4b","5a","5b","6a","6b","7a","7b","8a","8b","9a","9b","10a"],
        "min_sun":       6.0,
        "optimal_sun":   7.0,
        "nutrient_tags": ["prebiotic_compounds", "vitamin_c"],
        "spacing_m2":    0.1,
        "base_yield_kg": 0.15,
    },
    {
        "crop_id":       "beans",
        "crop_name":     "Green Beans",
        "usda_zones":    ["5a","5b","6a","6b","7a","7b","8a","8b","9a","9b","10a","10b"],
        "min_sun":       6.0,
        "optimal_sun":   8.0,
        "nutrient_tags": ["fiber", "folate", "magnesium"],
        "spacing_m2":    0.2,
        "base_yield_kg": 1.2,
    },
    {
        "crop_id":       "tomato",
        "crop_name":     "Tomato",
        "usda_zones":    ["6a","6b","7a","7b","8a","8b","9a","9b","10a","10b","11a"],
        "min_sun":       6.0,
        "optimal_sun":   8.0,
        "nutrient_tags": ["vitamin_c", "polyphenols"],
        "spacing_m2":    1.0,
        "base_yield_kg": 4.0,
    },
    {
        "crop_id":       "broccoli",
        "crop_name":     "Broccoli",
        "usda_zones":    ["5a","5b","6a","6b","7a","7b","8a","8b","9a","9b"],
        "min_sun":       4.0,
        "optimal_sun":   6.0,
        "nutrient_tags": ["vitamin_k", "vitamin_c", "fiber", "folate"],
        "spacing_m2":    0.5,
        "base_yield_kg": 0.5,
    },
    {
        "crop_id":       "beetroot",
        "crop_name":     "Beetroot",
        "usda_zones":    ["5a","5b","6a","6b","7a","7b","8a","8b","9a","9b","10a"],
        "min_sun":       4.0,
        "optimal_sun":   6.0,
        "nutrient_tags": ["folate", "fiber", "polyphenols"],
        "spacing_m2":    0.1,
        "base_yield_kg": 0.3,
    },
    {
        "crop_id":       "sweet_potato",
        "crop_name":     "Sweet Potato",
        "usda_zones":    ["8a","8b","9a","9b","10a","10b","11a"],
        "min_sun":       6.0,
        "optimal_sun":   8.0,
        "nutrient_tags": ["magnesium", "vitamin_c", "fiber"],
        "spacing_m2":    0.5,
        "base_yield_kg": 1.5,
    },
    {
        "crop_id":       "chard",
        "crop_name":     "Swiss Chard",
        "usda_zones":    ["5a","5b","6a","6b","7a","7b","8a","8b","9a","9b","10a","10b"],
        "min_sun":       4.0,
        "optimal_sun":   6.0,
        "nutrient_tags": ["vitamin_k", "magnesium", "vitamin_c"],
        "spacing_m2":    0.3,
        "base_yield_kg": 0.6,
    },
    {
        "crop_id":       "flaxseed",
        "crop_name":     "Flaxseed",
        "usda_zones":    ["5a","5b","6a","6b","7a","7b","8a","8b","9a"],
        "min_sun":       6.0,
        "optimal_sun":   7.0,
        "nutrient_tags": ["omega3_precursors", "fiber", "magnesium"],
        "spacing_m2":    0.1,
        "base_yield_kg": 0.2,
    },
    {
        "crop_id":       "blueberry",
        "crop_name":     "Blueberry",
        "usda_zones":    ["5a","5b","6a","6b","7a","7b","8a","8b"],
        "min_sun":       6.0,
        "optimal_sun":   8.0,
        "nutrient_tags": ["polyphenols", "vitamin_c", "fiber"],
        "spacing_m2":    1.5,
        "base_yield_kg": 2.0,
    },
    {
        "crop_id":       "onion",
        "crop_name":     "Onion",
        "usda_zones":    ["5a","5b","6a","6b","7a","7b","8a","8b","9a","9b","10a"],
        "min_sun":       6.0,
        "optimal_sun":   7.0,
        "nutrient_tags": ["prebiotic_compounds", "polyphenols"],
        "spacing_m2":    0.1,
        "base_yield_kg": 0.2,
    },
]


_GOAL_NUTRIENTS: dict[str, list[str]] = {
    "GUT":    ["fiber", "prebiotic_compounds", "polyphenols"],
    "ENERGY": ["magnesium", "vitamin_c", "folate"],
    "BONE":   ["vitamin_k", "magnesium", "omega3_precursors"],
}


@dataclass
class ScoredCrop:
    """A crop that passed filtering with its goal alignment score."""
    crop_id:        str
    crop_name:      str
    score:          int      # how many priority nutrients it matches
    nutrient_tags:  list[str]
    spacing_m2:     float
    base_yield_kg:  float
    optimal_sun:    float

def generate_crop_plan(
    garden_state: GardenState,
    health_target: str,
    top_n: int = 3,
) -> list[ScoredCrop]:
    """
    T006 — Deterministic Planning Engine
    Generates a ranked crop plan from garden constraints + health goal.

    Steps:
        1. Filter crops by USDA zone compatibility
        2. Filter crops by minimum sun requirement
        3. Score each crop by nutrient alignment with health goal
        4. Sort by score, return top N

    Args:
        garden_state:  Output of compute_garden_state() (T005)
        health_target: "GUT", "ENERGY", or "BONE"
        top_n:         How many crops to return (default 3)

    Returns:
        List of ScoredCrop objects, highest score first

    Example:
        state = compute_garden_state(37.7, -122.4, 6, "none", 12.0)
        plan  = generate_crop_plan(state, "GUT")
        plan[0].crop_name  → "Garlic"
        plan[0].score      → 2
    """
    target = health_target.upper().strip()
    priority_nutrients = _GOAL_NUTRIENTS.get(target, [])

    scored: list[ScoredCrop] = []

    for crop in _CROP_DB:

        # Step 1 — filter by USDA zone
        if garden_state.usda_zone not in crop["usda_zones"]:
            continue

        # Step 2 — filter by sun requirement
        if garden_state.adjusted_sun < crop["min_sun"]:
            continue

        # Step 3 — score by nutrient alignment
        # Count how many of the crop's nutrients match the goal's priority list
        matches = sum(
            1 for nutrient in crop["nutrient_tags"]
            if nutrient in priority_nutrients
        )

        scored.append(ScoredCrop(
            crop_id       = crop["crop_id"],
            crop_name     = crop["crop_name"],
            score         = matches,
            nutrient_tags = crop["nutrient_tags"],
            spacing_m2    = crop["spacing_m2"],
            base_yield_kg = crop["base_yield_kg"],
            optimal_sun   = crop["optimal_sun"],
        ))

    # Step 4 — sort by score descending, take top N
    scored.sort(key=lambda c: c.score, reverse=True)
    return scored[:top_n]


# ═══════════════════════════════════════════════════════════════════════════════
# T008 — YIELD BAND LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class YieldBand:
    """
    Realistic harvest range for one crop in one garden.
    Displayed to the user as "expect between X and Y kg this season".
    """
    crop_id:         str
    crop_name:       str
    plants_fit:      int
    adjusted_kg:     float   # baseline after sun modifier
    lower_kg:        float   # adjusted × 0.75
    upper_kg:        float   # adjusted × 1.25
    sun_modifier:    float   # how much sun affected yield


def calculate_yield_bands(
    crops:        list[ScoredCrop],
    garden_state: GardenState,
) -> list[YieldBand]:
    """
    T008 — Yield Band Logic
    Calculates realistic harvest ranges for each recommended crop.

    Formula (from Sprint 2 technical spec):
        plants      = garden_area ÷ spacing_per_plant
        base_yield  = kg_per_plant × plants
        sun_modifier = min(actual_sun ÷ optimal_sun, 1.0)
        adjusted    = base_yield × sun_modifier
        lower       = adjusted × 0.75   (−25%)
        upper       = adjusted × 1.25   (+25%)

    Args:
        crops:        Output of generate_crop_plan() (T006)
        garden_state: Output of compute_garden_state() (T005)

    Returns:
        List of YieldBand objects, one per crop

    Example:
        bands = calculate_yield_bands(plan, state)
        bands[0].lower_kg  → 9.8
        bands[0].upper_kg  → 16.4
    """
    bands: list[YieldBand] = []

    for crop in crops:
        # How many plants fit in the garden
        plants_fit = max(1, int(garden_state.garden_area_m2 / crop.spacing_m2))

        # Base yield for all plants
        base_yield = crop.base_yield_kg * plants_fit

        # Sun modifier — if actual sun < optimal, yield drops proportionally
        sun_modifier = min(garden_state.adjusted_sun / crop.optimal_sun, 1.0)
        sun_modifier = round(sun_modifier, 2)

        # Adjusted baseline
        adjusted = round(base_yield * sun_modifier, 1)

        # ±25% band
        lower = round(adjusted * 0.75, 1)
        upper = round(adjusted * 1.25, 1)

        bands.append(YieldBand(
            crop_id      = crop.crop_id,
            crop_name    = crop.crop_name,
            plants_fit   = plants_fit,
            adjusted_kg  = adjusted,
            lower_kg     = lower,
            upper_kg     = upper,
            sun_modifier = sun_modifier,
        ))

    return bands


# ═══════════════════════════════════════════════════════════════════════════════
# T007 — AI USAGE BOUNDARY MAP
# ═══════════════════════════════════════════════════════════════════════════════
# This is the governance config that defines where AI is and is not used.
# Every feature must appear here. Reviewed with Siva and Saina before build.

AI_BOUNDARY_MAP: dict[str, dict] = {

    "constraint_engine": {
        "uses_ai":   False,
        "rationale": "Deterministic zone + sun lookup. AI adds no accuracy benefit.",
    },
    "planning_engine": {
        "uses_ai":   False,
        "rationale": "Rule-based filtering and nutrient scoring. Fully explainable.",
    },
    "yield_band_logic": {
        "uses_ai":   False,
        "rationale": "Mathematical formula. Reproducibility requires no AI.",
    },
    "flora_ai_coach": {
        "uses_ai":     True,
        "model":       "claude-3-haiku / gpt-4o-mini",
        "token_limit": 500,
        "rationale":   "Natural language understanding needed for user queries.",
    },
    "garden_projection": {
        "uses_ai":     True,
        "model":       "FLUX image generation",
        "call_limit":  "1 per session",
        "rationale":   "AI image generation is the only way to produce realistic projections.",
    },
    "onboarding_tips": {
        "uses_ai":     True,
        "model":       "claude-3-haiku / gpt-4o-mini",
        "token_limit": 200,
        "rationale":   "Personalized tips benefit from language model.",
    },
    "nutrition_explanation": {
        "uses_ai":     True,
        "model":       "claude-3-haiku / gpt-4o-mini",
        "token_limit": 300,
        "rationale":   "Translating score logic into human-readable text.",
    },
}

# Hard cost ceiling per user session
# No session may exceed this regardless of features used
SESSION_AI_COST_CEILING_USD = 0.05  # 5 cents per session max


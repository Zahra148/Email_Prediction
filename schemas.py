# schemas.py
from __future__ import annotations
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field
from .constants import JobStatus, HealthTarget, NutrientCategory


# ── shared base classes (same in both versions) ───────────────────────────────

class Location(BaseModel):
    lat: float
    lng: float
    accuracy_m: Optional[float] = None

class Orientation(BaseModel):
    heading_deg: float = Field(ge=0, le=360)
    pitch_deg:   float = Field(ge=-90, le=90)
    roll_deg:    float = Field(ge=-180, le=180)


# ── HealthTargetProfile — MERGED version ──────────────────────────────────────
# Wentao's fields: target, priority, focus_areas, notes  (frontend uses these)
# Nayyab's fields: priority_nutrients, goal_match_weight  (scoring engine needs these)

class HealthTargetProfile(BaseModel):
    """
    A single health target with priority weight and nutrient mapping.
    Wentao's frontend fields + Nayyab's scoring fields merged together.
    """
    target:             HealthTarget
    priority:           float = Field(1.0, ge=0.0, le=1.0)
    focus_areas:        list[str] = []
    notes:              Optional[str] = None
    priority_nutrients: list[NutrientCategory] = []  # filled by get_health_target_profile()
    goal_match_weight:  float = 0.2                  # 20% of Longevity Score


class HealthProfileIn(BaseModel):
    """Raw intake form from the user. Wentao's version with backward compat."""
    user_id:           str
    health_targets:    list[HealthTargetProfile] = []
    health_goals:      list[str] = []   # backward-compat — kept intentionally
    contraindications: dict[str, Any] = {}
    diet:              dict[str, Any] = {}
    effort:            dict[str, Any] = {}
    schedule:          dict[str, Any] = {}


# ── GOAL_NUTRIENT_MAP — Nayyab's addition, needed for scoring ─────────────────
# Source: Health Intelligence Framework v2
# Maps each HealthTarget to its priority nutrients.
# Planning Engine uses this to rank crops by Goal Match Score.

GOAL_NUTRIENT_MAP: dict[HealthTarget, list[NutrientCategory]] = {
    HealthTarget.GUT: [
        NutrientCategory.FIBER,
        NutrientCategory.PREBIOTIC,
        NutrientCategory.POLYPHENOLS,
    ],
    HealthTarget.ENERGY: [
        NutrientCategory.MAGNESIUM,
        NutrientCategory.VITAMIN_C,
        NutrientCategory.FOLATE,
    ],
    HealthTarget.BONE: [
        NutrientCategory.VITAMIN_K,
        NutrientCategory.MAGNESIUM,
        NutrientCategory.OMEGA3_PRECURSORS,
    ],
}


def get_health_target_profile(target: str) -> HealthTargetProfile:
    """
    Returns a HealthTargetProfile for a given target string.
    Accepts both uppercase ("GUT") and lowercase ("gut").

    Usage:
        profile = get_health_target_profile("GUT")
        profile.priority_nutrients
        # → [FIBER, PREBIOTIC, POLYPHENOLS]
    """
    try:
        key = HealthTarget(target.upper().strip())
    except ValueError:
        valid = [t.value for t in HealthTarget]
        raise ValueError(f"Unknown target '{target}'. Must be one of: {valid}")

    labels = {
        HealthTarget.ENERGY: "Energy",
        HealthTarget.GUT:    "Gut Health",
        HealthTarget.BONE:   "Bone Strength",
    }

    return HealthTargetProfile(
        target             = key,
        priority           = 1.0,
        priority_nutrients = GOAL_NUTRIENT_MAP[key],
        goal_match_weight  = 0.2,
        notes              = labels[key],
    )


# ── Wentao's new schemas — keeping all of them ────────────────────────────────

class GardenCreateIn(BaseModel):
    name:     str
    location: Location

class IntakeInput(BaseModel):
    type:       Literal["image", "video"]
    object_key: str
    width:      Optional[int] = None
    height:     Optional[int] = None
    mime:       Optional[str] = None

class GardenIntakeIn(BaseModel):
    garden_id:    str
    capture_mode: Literal["photo", "video"]
    timestamp:    str
    orientation:  Orientation
    device:       dict[str, Any] = {}
    inputs:       list[IntakeInput]

class PerceptionRunIn(BaseModel):
    garden_id:         str
    intake_id:         str
    outputs_requested: list[str] = ["segmentation", "sun_hints", "geometry_hints"]

class MicroclimateIn(BaseModel):
    garden_id: str
    location:  Location

class HealthCompileIn(BaseModel):
    garden_id:  str
    profile_id: str

class TargetExplanation(BaseModel):
    """Per-target explanation returned by the health-compile endpoint."""
    target:        HealthTarget
    why:           str
    top_nutrients: list[str]

class HealthCompileOut(BaseModel):
    """Typed response for POST /v1/health/intelligence/compile."""
    scoring_profile_id: str
    nutrient_weights:   dict[str, float]
    pillar_weights:     dict[str, float]
    crop_constraints:   dict[str, list[str]]
    explanations:       list[TargetExplanation]

class ConstraintsComputeIn(BaseModel):
    garden_id:          str
    intake_id:          str
    perception_id:      str
    microclimate_id:    str
    scoring_profile_id: str
    guardrails:         dict[str, Any] = {}

class PlanGenerateIn(BaseModel):
    garden_id:          str
    constraint_id:      str
    inventory:          dict[str, Any]
    existing_plants:    list[str] = []
    time_horizon_weeks: int = 12

class PlanMetrics(BaseModel):
    """MVP metrics required for demo. Wentao's addition."""
    nutrition_score:       int
    estimated_savings_usd: float

class PlanResponse(BaseModel):
    """Full plan response. Wentao's addition."""
    plan_id:              str
    summary:              dict[str, Any] = {}
    beds:                 list[dict[str, Any]] = []
    schedule:             list[dict[str, Any]] = []
    yield_bands:          list[dict[str, Any]] = []
    nutrition_projection: dict[str, Any] = {}
    metrics:              PlanMetrics

class BehaviorNextActionIn(BaseModel):
    user_id:       str
    garden_id:     str
    plan_id:       str
    today_context: dict[str, Any] = {}

class RenderGenerateIn(BaseModel):
    garden_id:            str
    plan_id:              str
    intake_id:            str
    style:                str = "photorealistic"
    inputs:               dict[str, str]
    constraints_snapshot: dict[str, Any] = {}

class EventIn(BaseModel):
    user_id:    str
    garden_id:  Optional[str] = None
    session_id: Optional[str] = None
    name:       str
    properties: dict[str, Any] = {}
    timestamp:  str

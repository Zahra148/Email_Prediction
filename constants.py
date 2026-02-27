# constants.py
from enum import Enum

class StrEnum(str, Enum):
    pass

class JobStatus(StrEnum):
    QUEUED   = "QUEUED"
    RUNNING  = "RUNNING"
    DONE     = "DONE"
    FAILED   = "FAILED"

class UserStateEnum(StrEnum):
    OVERWHELMED = "OVERWHELMED"
    CURIOUS     = "CURIOUS"
    MOTIVATED   = "MOTIVATED"
    CONSISTENT  = "CONSISTENT"
    AT_RISK     = "AT_RISK"

class EventName(StrEnum):
    PLAN_VIEWED          = "PLAN_VIEWED"
    MICRO_TASK_ASSIGNED  = "MICRO_TASK_ASSIGNED"
    MICRO_TASK_COMPLETED = "MICRO_TASK_COMPLETED"
    RENDER_STARTED       = "RENDER_STARTED"
    RENDER_PREVIEW_READY = "RENDER_PREVIEW_READY"
    RENDER_DONE          = "RENDER_DONE"

class HealthTarget(StrEnum):
    """Typed health-target categories. Uppercase to match frontend."""
    GUT    = "GUT"
    BONE   = "BONE"
    ENERGY = "ENERGY"

class NutrientCategory(StrEnum):
    FIBER             = "fiber"
    POLYPHENOLS       = "polyphenols"
    VITAMIN_K         = "vitamin_k"
    MAGNESIUM         = "magnesium"
    VITAMIN_C         = "vitamin_c"
    OMEGA3_PRECURSORS = "omega3_precursors"
    FOLATE            = "folate"
    PREBIOTIC         = "prebiotic_compounds"

"""
LinkedIn Post Refiner Utilities Package
"""

from .similarity import (
    compute_similarity,
    compute_edit_percentage,
    compute_jaccard_similarity,
    validate_originality,
    SIM_SCORE_THRESHOLD,
    EDIT_PCT_THRESHOLD,
)
from .security import (
    redact_pii,
    get_api_key,
    mask_api_key,
    RateLimiter,
    check_rate_limit,
    default_rate_limiter,
)

__all__ = [
    # Similarity
    "compute_similarity",
    "compute_edit_percentage",
    "compute_jaccard_similarity",
    "validate_originality",
    "SIM_SCORE_THRESHOLD",
    "EDIT_PCT_THRESHOLD",
    # Security
    "redact_pii",
    "get_api_key",
    "mask_api_key",
    "RateLimiter",
    "check_rate_limit",
    "default_rate_limiter",
]

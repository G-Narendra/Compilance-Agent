"""
utils/helpers.py - small utility functions that don't belong anywhere else.
"""

import hashlib
from datetime import datetime, timezone


def now_utc() -> datetime:
    """current time in utc. we always use utc internally."""
    return datetime.now(timezone.utc)


def hash_text(text: str) -> str:
    """quick sha256 hash for deduplication or caching keys."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def truncate(text: str, max_len: int = 500) -> str:
    """truncate text with ellipsis. useful for logging and previews."""
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def estimate_tokens(text: str) -> int:
    """
    rough token count estimate. 
    not perfect but good enough for checking limits before hitting the api.
    real count depends on the tokenizer but ~4 chars per token is a decent guess.
    """
    return len(text) // 4


def format_score(score: float | None) -> str:
    """format a compliance score for display."""
    if score is None:
        return "N/A"
    if score >= 80:
        return f"✅ {score:.0f}/100"
    elif score >= 50:
        return f"⚠️ {score:.0f}/100"
    else:
        return f"❌ {score:.0f}/100"

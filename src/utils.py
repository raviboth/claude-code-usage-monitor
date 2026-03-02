"""Shared utility functions used across the UI layer."""

from collections.abc import Callable
from datetime import datetime, timezone

from src.constants import (
    COLOR_GREEN,
    COLOR_GREY,
    COLOR_RED,
    COLOR_YELLOW,
    THRESHOLD_RED,
    THRESHOLD_YELLOW,
)


def color_for_utilization(utilization: float | None) -> str:
    """Return a hex color string based on utilization level."""
    if utilization is None:
        return COLOR_GREY
    if utilization >= THRESHOLD_RED:
        return COLOR_RED
    if utilization >= THRESHOLD_YELLOW:
        return COLOR_YELLOW
    return COLOR_GREEN


def format_utilization(utilization: float) -> str:
    """Format utilization as a percentage string like '42%' or '100+%'."""
    pct = int(utilization * 100)
    if pct > 100:
        return "100+%"
    return f"{pct}%"


def format_utilization_label(utilization: float | None) -> str:
    """Format utilization as a short label for tray icons ('42', '100+', '?')."""
    if utilization is None:
        return "?"
    pct = int(utilization * 100)
    if pct > 100:
        return "100+"
    return str(pct)


def format_reset_time(resets_at: datetime | None) -> str:
    """Format a reset time as a relative countdown string (e.g. 'resets in 2h 15m')."""
    if resets_at is None:
        return "no reset scheduled"
    now = datetime.now(timezone.utc)
    delta = resets_at - now
    if delta.total_seconds() <= 0:
        return "resetting now"
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes = remainder // 60
    parts: list[str] = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0 and days == 0:
        parts.append(f"{minutes}m")
    return f"resets in {' '.join(parts)}" if parts else "resets soon"


def format_reset_time_verbose(resets_at: datetime | None) -> str:
    """Format a reset time with both relative countdown and absolute time.

    Used in the dashboard where more detail is helpful.
    """
    if resets_at is None:
        return "No reset scheduled"
    now = datetime.now(timezone.utc)
    delta = resets_at - now
    if delta.total_seconds() <= 0:
        return "Resetting now"

    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes = remainder // 60

    parts: list[str] = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0 and days == 0:
        parts.append(f"{minutes}m")
    relative = " ".join(parts) if parts else "soon"

    local_reset = resets_at.astimezone()
    if days == 0:
        absolute = local_reset.strftime("%-I:%M %p today")
    elif days < 7:
        absolute = local_reset.strftime("%a at %-I:%M %p")
    else:
        absolute = local_reset.strftime("%b %-d at %-I:%M %p")

    return f"Resets in {relative} \u00b7 {absolute}"

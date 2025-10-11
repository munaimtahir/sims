"""Service layer for advanced analytics computations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Dict, Iterable, List, Optional, Sequence

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import models
from django.db.models import (
    Avg,
    Count,
    DurationField,
    ExpressionWrapper,
    F,
    Max,
    QuerySet,
)

from sims.logbook.models import LogbookEntry

User = get_user_model()

ALLOWED_WINDOWS: Sequence[int] = (7, 30, 90)
CACHE_TIMEOUT_SECONDS = 300


@dataclass(frozen=True)
class TrendRequest:
    """Parameters for building trend analytics."""

    window: int
    metric: str = "entries"
    include_moving_average: bool = True

    def cache_key(self, user_id: int, extra_filters: Optional[str] = None) -> str:
        suffix = f"::{extra_filters}" if extra_filters else ""
        return f"analytics:trend:{user_id}:{self.metric}:{self.window}{suffix}"


def validate_window(raw_window: Optional[str]) -> int:
    """Validate and normalise the rolling window parameter."""

    window = 30 if raw_window is None else int(raw_window)
    if window not in ALLOWED_WINDOWS:
        raise ValueError(f"Window must be one of {', '.join(map(str, ALLOWED_WINDOWS))}")
    return window


def get_accessible_users(user: User) -> QuerySet[User]:
    """Return a queryset of users visible to the acting user."""

    if user.is_superuser or getattr(user, "role", None) == "admin":
        return User.objects.all()
    if getattr(user, "role", None) == "supervisor":
        return User.objects.filter(models.Q(id=user.id) | models.Q(supervisor=user))
    return User.objects.filter(id=user.id)


def _base_logbook_queryset() -> QuerySet[LogbookEntry]:
    return (
        LogbookEntry.objects.select_related("pg", "supervisor", "rotation")
        .prefetch_related("procedures", "skills")
        .all()
    )


def trend_for_user(
    acting_user: User,
    target_user: User,
    params: TrendRequest,
    status_filter: Optional[Sequence[str]] = None,
) -> Dict[str, List[Dict[str, Optional[float]]]]:
    """Compute a rolling trend for a user with caching."""

    from django.db.models import Q

    if target_user not in get_accessible_users(acting_user):
        raise PermissionError("You do not have permission to view this user's analytics.")

    cache_key = params.cache_key(
        target_user.pk, extra_filters="|".join(status_filter) if status_filter else None
    )
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    window_delta = params.window - 1
    queryset = _base_logbook_queryset().filter(pg=target_user)
    if status_filter:
        queryset = queryset.filter(status__in=status_filter)

    latest_entry_date = queryset.aggregate(max_date=Max("date"))["max_date"]
    if latest_entry_date is None:
        payload = {"series": [], "window": params.window, "metric": params.metric}
        cache.set(cache_key, payload, CACHE_TIMEOUT_SECONDS)
        return payload

    start_date = latest_entry_date - timedelta(days=window_delta)
    queryset = queryset.filter(date__gte=start_date)

    daily_counts = (
        queryset.values("date")
        .annotate(
            value=Count("id"),
            approved=Count("id", filter=Q(status="approved")),
            avg_score=Avg("supervisor_assessment_score"),
        )
        .order_by("date")
    )

    series: List[Dict[str, Optional[float]]] = []
    rolling_window: List[int] = []

    for bucket in daily_counts:
        bucket_date = bucket["date"]
        count = int(bucket["value"])
        rolling_window.append(count)
        if len(rolling_window) > params.window:
            rolling_window.pop(0)
        moving_average = (
            sum(rolling_window) / len(rolling_window) if params.include_moving_average else None
        )
        series.append(
            {
                "date": bucket_date.isoformat(),
                "count": count,
                "approved": int(bucket["approved"]),
                "avg_score": (
                    float(bucket["avg_score"]) if bucket["avg_score"] is not None else None
                ),
                "moving_average": (
                    round(moving_average, 2) if moving_average is not None else None
                ),
            }
        )

    payload: Dict[str, List[Dict[str, Optional[float]]]] = {
        "series": series,
        "window": params.window,
        "metric": params.metric,
    }
    cache.set(cache_key, payload, CACHE_TIMEOUT_SECONDS)
    return payload


def comparative_summary(
    acting_user: User,
    primary_users: Iterable[User],
    secondary_users: Iterable[User],
    metric: str = "entries",
) -> Dict[str, Dict[str, float]]:
    """Build comparative analytics between two groups of users."""

    allowed_users = get_accessible_users(acting_user)
    allowed_ids = set(allowed_users.values_list("id", flat=True))
    primary_ids = [user.pk for user in primary_users if user.pk in allowed_ids]
    secondary_ids = [user.pk for user in secondary_users if user.pk in allowed_ids]

    if not primary_ids:
        raise PermissionError("No primary users available with your permissions.")
    if not secondary_ids:
        raise PermissionError("No secondary users available with your permissions.")

    queryset = _base_logbook_queryset()

    aggregates = {
        "primary": _comparative_block(queryset, primary_ids, metric),
        "secondary": _comparative_block(queryset, secondary_ids, metric),
    }
    return aggregates


def _comparative_block(
    queryset: QuerySet[LogbookEntry], user_ids: Sequence[int], metric: str
) -> Dict[str, float]:
    subset = queryset.filter(pg_id__in=user_ids)
    total_entries = subset.count()
    approved_count = subset.filter(status="approved").count()
    average_score = subset.aggregate(avg=Avg("supervisor_assessment_score"))["avg"] or 0.0
    if metric == "approval_rate":
        value: float = approved_count / total_entries if total_entries else 0.0
    elif metric == "avg_score":
        value = float(average_score)
    else:
        value = float(total_entries)

    return {
        "value": round(value, 2),
        "total_entries": total_entries,
        "approved": approved_count,
        "average_score": round(float(average_score), 2) if average_score else 0.0,
    }


def performance_metrics(
    acting_user: User, queryset: Optional[QuerySet[LogbookEntry]] = None
) -> Dict[str, float]:
    """Return KPI style metrics for the performance dashboard."""

    if queryset is None:
        accessible_users = get_accessible_users(acting_user)
        queryset = _base_logbook_queryset().filter(pg__in=accessible_users)

    total_entries = queryset.count()
    pending = queryset.filter(status="pending").count()
    approved = queryset.filter(status="approved").count()
    rejected = queryset.filter(status="rejected").count()

    review_durations = queryset.filter(
        submitted_to_supervisor_at__isnull=False, supervisor_action_at__isnull=False
    ).annotate(
        review_duration=ExpressionWrapper(
            F("supervisor_action_at") - F("submitted_to_supervisor_at"),
            output_field=DurationField(),
        )
    )
    average_review_hours = 0.0
    if review_durations.exists():
        total_seconds = sum(
            duration["review_duration"].total_seconds()
            for duration in review_durations.values("review_duration")
        )
        average_review_hours = round(total_seconds / (len(review_durations) * 3600), 2)

    approval_rate = round(approved / total_entries, 2) if total_entries else 0.0
    rejection_rate = round(rejected / total_entries, 2) if total_entries else 0.0
    pending_rate = round(pending / total_entries, 2) if total_entries else 0.0

    return {
        "total_entries": float(total_entries),
        "pending": float(pending),
        "approved": float(approved),
        "approval_rate": approval_rate,
        "rejection_rate": rejection_rate,
        "pending_rate": pending_rate,
        "average_review_hours": average_review_hours,
    }


__all__ = [
    "TrendRequest",
    "trend_for_user",
    "comparative_summary",
    "performance_metrics",
    "validate_window",
    "get_accessible_users",
]

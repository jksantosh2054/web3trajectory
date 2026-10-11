"""Analytics privacy helpers: cohort minimums + sparse-cell suppression.

Policy (design §12.2): aggregation-first; minimum 30 distinct actors per
released bucket; sparse cells suppressed; precise event coordinates never
released; repeated overlapping queries budgeted.
"""
from __future__ import annotations

MIN_COHORT = 30


def check_cohort_minimum(distinct_actors: int, minimum: int = MIN_COHORT) -> bool:
    """True if a bucket may be released."""
    return distinct_actors >= minimum


def apply_suppression(
    buckets: list[dict], cohort_key: str = "distinct_actors", minimum: int = MIN_COHORT
) -> tuple[list[dict], list[str]]:
    """Split buckets into releasable vs suppressed.

    Returns (released, suppressed_bucket_ids). Suppressed cells are reported
    in the snapshot privacy_report so the creator sees exactly what was hidden.
    """
    released: list[dict] = []
    suppressed: list[str] = []
    for b in buckets:
        if check_cohort_minimum(int(b.get(cohort_key, 0)), minimum):
            released.append(b)
        else:
            suppressed.append(str(b.get("bucket_id", "?")))
    return released, suppressed


def teaser_band(total_views: int) -> str:
    """Coarse engagement band for public teasers — never exact counts."""
    if total_views < 100:
        return "<100 views"
    if total_views < 1_000:
        return "100–1k views"
    if total_views < 5_000:
        return "1k–5k views"
    if total_views < 50_000:
        return "5k–50k views"
    return "50k+ views"

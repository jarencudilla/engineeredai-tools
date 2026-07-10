"""
analyzers/gsc_opportunities.py

Deterministic analysis (spec Phase 3): finds pages/queries getting
seen but not clicked — the "why is this getting impressions but no
clicks" question from the spec's own list of things Site Kit and
GA4 don't answer directly.

Analyzers only analyze — this takes rows already in the database
and returns a filtered, scored subset. It never fetches or stores
anything itself.
"""

from dataclasses import dataclass


@dataclass
class Opportunity:
    """
    One row flagged as a CTR opportunity: real visibility (impressions),
    weak click-through relative to that visibility.

    @param query        The search query.
    @param page         The page it matched to.
    @param impressions  Total impressions.
    @param clicks       Total clicks.
    @param ctr          Click-through rate, 0.0–1.0.
    @param position     Average search position.
    @param severity     "high" | "medium" — how strong the opportunity is,
                         based on how much impression volume is being wasted.
    """
    query: str
    page: str
    impressions: int
    clicks: int
    ctr: float
    position: float
    severity: str


def find_ctr_opportunities(
    gsc_rows,
    min_impressions: int = 5,
    max_ctr: float = 0.02,
) -> list[Opportunity]:
    """
    Filter stored GSC rows down to queries with real visibility but
    weak click-through — the highest-leverage place to improve a
    title or meta description, since the query is already ranking
    and being seen.

    @param gsc_rows        list[sqlite3.Row]  Output of database.db.fetch_all_queries
    @param min_impressions int    Floor for "real visibility" (default 5 —
                                   below this, low CTR is just noise from
                                   a tiny sample size, not a signal)
    @param max_ctr          float  Ceiling for "weak click-through" (default
                                   2% — below typical CTR at any position
                                   under ~30, see position-based CTR curves)
    @return list[Opportunity]  Sorted by impressions descending — the
                                biggest wasted-visibility rows first.
    """
    opportunities = []

    for row in gsc_rows:
        impressions = row["impressions"]
        ctr = row["ctr"]

        if impressions < min_impressions or ctr > max_ctr:
            continue

        # NOTE: severity is a simple volume threshold for now — a
        # page with 50 impressions and 0% CTR is a bigger miss than
        # one with 6 impressions and 0% CTR, even though both pass
        # the raw filter above.
        severity = "high" if impressions >= 20 else "medium"

        opportunities.append(
            Opportunity(
                query=row["query"],
                page=row["page"],
                impressions=impressions,
                clicks=row["clicks"],
                ctr=ctr,
                position=row["position"],
                severity=severity,
            )
        )

    opportunities.sort(key=lambda o: o.impressions, reverse=True)
    return opportunities

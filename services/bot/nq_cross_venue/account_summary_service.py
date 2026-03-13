"""Venue account summary aggregation from snapshots (and future API)."""
from __future__ import annotations

import os
from datetime import datetime
from typing import Any

from nq_cross_venue.models import DashboardAggregationContract, SeparatedCapitalView, VenueAccountSummary, VenueSummary


def _dsn() -> str:
    return os.getenv("PG_DSN", "postgresql://nebula:nebula123@localhost:5432/trading")


class VenueAccountSummaryService:
    """Aggregate venue account summaries from venue_account_snapshot; build dashboard contract."""

    def get_latest_per_venue(self) -> list[VenueAccountSummary]:
        """Fetch latest snapshot per venue from venue_account_snapshot."""
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError:
            return []
        out = []
        with psycopg.connect(_dsn(), row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT DISTINCT ON (venue) venue, account_id, balance, equity, created_at
                    FROM venue_account_snapshot
                    ORDER BY venue, created_at DESC
                    """
                )
                for r in cur.fetchall():
                    out.append(
                        VenueAccountSummary(
                            venue_id=r["venue"],
                            account_id=r["account_id"],
                            balance=float(r["balance"]) if r["balance"] is not None else None,
                            equity=float(r["equity"]) if r["equity"] is not None else None,
                            updated_at=r["created_at"],
                            meta={},
                        )
                    )
        return out

    def build_dashboard_contract(
        self,
        venues: list[VenueSummary] | None = None,
    ) -> DashboardAggregationContract:
        """Build aggregation contract for control plane / UI."""
        if venues is None:
            from nq_cross_venue.venue_service import VenueAbstractionService
            venues = VenueAbstractionService().list_venues()
        summaries = self.get_latest_per_venue()
        by_venue = {s.venue_id: s for s in summaries}
        separated: list[SeparatedCapitalView] = []
        total_equity = 0.0
        for v in venues:
            s = by_venue.get(v.venue_id)
            bal = s.balance if s else 0.0
            eq = s.equity if s else 0.0
            separated.append(SeparatedCapitalView(venue_id=v.venue_id, balance=bal, equity=eq, allocated=bal, meta={}))
            total_equity += eq
        return DashboardAggregationContract(
            venues=venues,
            account_summaries=summaries,
            separated_capital=separated,
            total_equity=total_equity,
            meta={},
        )

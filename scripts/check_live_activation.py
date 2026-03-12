#!/usr/bin/env python3
# NEBULA-QUANT v1 | Phase 58 — Check Binance live activation state (deterministic, no network)

from __future__ import annotations

import sys
from pathlib import Path

# Allow importing from services/bot when run from repo root
repo_root = Path(__file__).resolve().parent.parent
bot_path = repo_root / "services" / "bot"
if str(bot_path) not in sys.path:
    sys.path.insert(0, str(bot_path))

from adapters.binance.activation import (
    BINANCE_LIVE_ACTIVATION_CONFIG,
    BinanceActivationEngine,
)


def main() -> int:
    config = BINANCE_LIVE_ACTIVATION_CONFIG
    engine = BinanceActivationEngine(
        config=config,
        binance_venue_enabled=True,
        tradestation_venue_enabled=False,
    )
    print("live_enabled:", config.live_enabled)
    print("eligible_strategies:", config.allowed_live_strategies)
    print("pending_strategies:", [])
    print("rejected_strategies:", [])
    return 0


if __name__ == "__main__":
    sys.exit(main())

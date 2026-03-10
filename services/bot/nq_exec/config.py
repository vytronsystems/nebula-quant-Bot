# NEBULA-QUANT v1 | nq_exec config — simulated/non-live defaults

# Execution mode: "simulated" = in-memory only, no live broker.
DEFAULT_EXECUTION_MODE: str = "simulated"

# Order type when not specified: "market" or "limit".
DEFAULT_ORDER_TYPE: str = "market"

# Broker identifier for routing; "none" = no real broker.
DEFAULT_BROKER: str = "none"

# When False, engine rejects all orders (fail-closed). No simulated fill.
DEFAULT_EXECUTION_ENABLED: bool = False

# Placeholder fill price: "limit" = use order limit_price, "close" = caller passes price.
DEFAULT_SIMULATED_FILL_PRICE_MODE: str = "limit"

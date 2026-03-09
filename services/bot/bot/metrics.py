from prometheus_client import start_http_server, Counter, Gauge

# Métricas mínimas
HEARTBEATS_TOTAL = Counter("nq_heartbeats_total", "Total heartbeats emitted by the bot")
SNAPSHOTS_TOTAL  = Counter("nq_snapshots_total", "Total decision snapshots written")
BOT_UP           = Gauge("nq_bot_up", "Bot process up")

def metrics_start(port: int = 8080) -> None:
    # No bloquea; arranca servidor en hilo interno
    start_http_server(port, addr="0.0.0.0")
    BOT_UP.set(1)

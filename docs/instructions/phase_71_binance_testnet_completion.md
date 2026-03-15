NEBULA-QUANT v1 | Phase 71 — Complete Binance Testnet Integration

Objective:
Finish full Binance Futures Testnet connectivity.

Requirements:
1. Validate connection using:
- account balance
- BTCUSDT price
- orderbook
- trades
- open orders
- positions

2. Add WebSocket stream for:
- mark price
- trades
- orderbook depth

3. Add connectivity health status.

4. Expose endpoints required by UI.

5. Ensure safe degraded behavior if credentials missing.

Tests:
- connectivity
- market data
- account retrieval
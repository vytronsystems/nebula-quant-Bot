import uuid
from datetime import datetime
from sqlalchemy import (
    DateTime, ForeignKey, Integer, Numeric, String, Text, JSON, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

def utcnow() -> datetime:
    return datetime.utcnow()

class BotRun(Base):
    __tablename__ = "bot_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=utcnow, nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    env: Mapped[str] = mapped_column(String(32), default="local", nullable=False)
    version: Mapped[str] = mapped_column(String(64), default="dev", nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="running", nullable=False)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    snapshots: Mapped[list["DecisionSnapshot"]] = relationship(back_populates="bot_run")


class DecisionSnapshot(Base):
    __tablename__ = "decision_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    bot_run_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("bot_runs.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=utcnow, nullable=False)

    symbol: Mapped[str] = mapped_column(String(16), nullable=False, default="QQQ")
    timeframe: Mapped[str] = mapped_column(String(16), nullable=False, default="5m")
    session_tag: Mapped[str] = mapped_column(String(32), nullable=False, default="regular")

    decision: Mapped[str] = mapped_column(String(24), nullable=False)  # trade/no_trade/reject
    direction: Mapped[str | None] = mapped_column(String(8), nullable=True)  # call/put
    confidence: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0-100

    policy_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    user_params: Mapped[dict] = mapped_column(JSON, nullable=False)
    derived_params: Mapped[dict] = mapped_column(JSON, nullable=False)

    indicators: Mapped[dict] = mapped_column(JSON, nullable=False)
    levels: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    news_context: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    contract: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    reason_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reason_detail: Mapped[str | None] = mapped_column(Text, nullable=True)

    bot_run: Mapped["BotRun"] = relationship(back_populates="snapshots")


Index("ix_decision_snapshots_created_at", DecisionSnapshot.created_at)
Index("ix_decision_snapshots_symbol_created_at", DecisionSnapshot.symbol, DecisionSnapshot.created_at)


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=utcnow, nullable=False)

    broker: Mapped[str] = mapped_column(String(24), default="tradestation", nullable=False)
    account_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)

    side: Mapped[str] = mapped_column(String(8), nullable=False)   # buy/sell
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    order_type: Mapped[str] = mapped_column(String(16), nullable=False)  # market/limit
    limit_price: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)

    status: Mapped[str] = mapped_column(String(16), default="new", nullable=False)
    broker_order_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    raw_request: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    raw_response: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class Execution(Base):
    __tablename__ = "executions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=utcnow, nullable=False)

    order_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=True)
    broker_exec_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    qty: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    price: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)

    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class Trade(Base):
    __tablename__ = "trades"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=utcnow, nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)

    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    direction: Mapped[str] = mapped_column(String(16), nullable=False)  # call/put/spread
    qty: Mapped[int] = mapped_column(Integer, nullable=False)

    entry_price: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    exit_price: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)

    pnl_usd: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    rr: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)

    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class ErrorLog(Base):
    __tablename__ = "errors"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=utcnow, nullable=False)

    component: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), default="error", nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)

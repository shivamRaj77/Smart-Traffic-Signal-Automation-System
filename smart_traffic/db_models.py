"""SQLAlchemy ORM models for application persistence."""

from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False, default="user")
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)


class SignalOverrideORM(Base):
    __tablename__ = "signal_overrides"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    junction_id: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    green_time: Mapped[int] = mapped_column(Integer, nullable=False)
    set_by: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)


class SimulationLogORM(Base):
    __tablename__ = "simulation_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    avg_congestion: Mapped[float] = mapped_column(nullable=False)
    critical_junction: Mapped[str] = mapped_column(String(16), nullable=False)
    critical_congestion: Mapped[float] = mapped_column(nullable=False)
    triggered_by: Mapped[str] = mapped_column(String(64), nullable=False)

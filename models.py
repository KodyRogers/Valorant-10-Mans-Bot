from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    Boolean
)
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


# =========================
# Player Table
# =========================
class Player(Base):
    __tablename__ = "players"

    # Discord User ID
    discord_id = Column(String, primary_key=True)

    # Riot Information
    riot_name = Column(String, nullable=False)
    riot_tag = Column(String, nullable=False)

    # Ranking / Stats
    elo = Column(Integer, default=1000)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)

    # Queue status
    is_queued = Column(Boolean, default=False)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    match_entries = relationship("MatchPlayer", back_populates="player")


# =========================
# Match Table
# =========================
class Match(Base):
    __tablename__ = "matches"

    # Unique match ID
    match_id = Column(Integer, primary_key=True, autoincrement=True)

    # Match metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Team results
    winning_team = Column(Integer, nullable=True)  # 1 or 2

    # Optional map info
    map_name = Column(String, nullable=True)

    # Relationships
    players = relationship("MatchPlayer", back_populates="match")


# =========================
# Match Player Stats Table
# =========================
class MatchPlayer(Base):
    __tablename__ = "match_players"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    match_id = Column(Integer, ForeignKey("matches.match_id"))
    discord_id = Column(String, ForeignKey("players.discord_id"))

    # Team Assignment
    team = Column(Integer, nullable=False)  # Team 1 or Team 2

    # Performance Stats
    kills = Column(Integer, default=0)
    deaths = Column(Integer, default=0)
    assists = Column(Integer, default=0)

    # ELO change after match
    elo_change = Column(Integer, default=0)

    # Relationships
    match = relationship("Match", back_populates="players")
    player = relationship("Player", back_populates="match_entries")


# =========================
# Queue Table
# =========================
class Queue(Base):
    __tablename__ = "queue"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Discord User
    discord_id = Column(String, ForeignKey("players.discord_id"))

    # Queue join time
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Optional role (captain, fill, etc.)
    role = Column(String, nullable=True)
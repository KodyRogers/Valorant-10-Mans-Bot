from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String
)
from sqlalchemy.orm import relationship

from database import Base


# ===================================
# PLAYER
# ===================================
class Player(Base):
    __tablename__ = "players"

    # Discord Account
    discord_id = Column(
        String,
        primary_key=True
    )

    # Riot Information
    riot_name = Column(
        String,
        nullable=False
    )

    riot_tag = Column(
        String,
        nullable=False
    )

    # Permanent Riot Identifier
    # Never changes even if Riot ID changes.
    puuid = Column(
        String,
        unique=True,
        nullable=False
    )

    # Player Statistics
    elo = Column(
        Integer,
        default=1000
    )

    wins = Column(
        Integer,
        default=0
    )

    losses = Column(
        Integer,
        default=0
    )

    # Queue State
    is_queued = Column(
        Boolean,
        default=False
    )

    # Current active match
    current_match = Column(
        Integer,
        ForeignKey("matches.match_id"),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationships
    match_entries = relationship(
        "MatchPlayer",
        back_populates="player"
    )


# ===================================
# MATCH
# ===================================
class Match(Base):
    __tablename__ = "matches"

    # Internal Database ID
    match_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # Public Match Code
    match_code = Column(
        String,
        unique=True,
        nullable=False
    )

    # Drafting
    # Live
    # Completed
    # Cancelled
    status = Column(
        String,
        default="Waiting"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )

    # Captains
    captain_1 = Column(
        String,
        ForeignKey("players.discord_id"),
        nullable=True
    )

    captain_2 = Column(
        String,
        ForeignKey("players.discord_id"),
        nullable=True
    )

    # Team Names
    team_1_name = Column(
        String,
        default="Team 1"
    )

    team_2_name = Column(
        String,
        default="Team 2"
    )

    # Match Information
    selected_map = Column(
        String,
        nullable=True
    )

    winning_team = Column(
        Integer,
        nullable=True
    )

    # Website URL
    draft_url = Column(
        String,
        nullable=True
    )

    players = relationship(
        "MatchPlayer",
        back_populates="match"
    )


# ===================================
# MATCH PLAYER
# ===================================
class MatchPlayer(Base):
    __tablename__ = "match_players"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    match_id = Column(
        Integer,
        ForeignKey("matches.match_id")
    )

    discord_id = Column(
        String,
        ForeignKey("players.discord_id")
    )

    # Team Assignment
    team = Column(
        Integer,
        nullable=True
    )

    # Draft Information
    is_captain = Column(
        Boolean,
        default=False
    )

    pick_order = Column(
        Integer,
        nullable=True
    )

    # Match Statistics
    kills = Column(
        Integer,
        default=0
    )

    deaths = Column(
        Integer,
        default=0
    )

    assists = Column(
        Integer,
        default=0
    )

    elo_change = Column(
        Integer,
        default=0
    )

    match = relationship(
        "Match",
        back_populates="players"
    )

    player = relationship(
        "Player",
        back_populates="match_entries"
    )


# ===================================
# QUEUE
# ===================================
class Queue(Base):
    __tablename__ = "queue"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    discord_id = Column(
        String,
        ForeignKey("players.discord_id"),
        nullable=False
    )

    joined_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    role = Column(
        String,
        nullable=True
    )
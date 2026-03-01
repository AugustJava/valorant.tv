from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date, BigInteger
from sqlalchemy.orm import relationship
import datetime
from database import Base 

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)

class NewsModel(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    summary = Column(String)
    content = Column(String)
    author = Column(String)
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class TeamModel(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    team = Column(String, unique=True, index=True)
    region = Column(String, index=True)
    logo_url = Column(String, nullable=True)  # Ссылка на картинку
    is_active = Column(Boolean, default=True) # Играет ли команда сейчас

class MatchModel(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    # Ссылаемся на id из таблицы teams
    team_home_id = Column(Integer, ForeignKey("teams.id"))
    team_away_id = Column(Integer, ForeignKey("teams.id"))

    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    
    team_home_score = Column(Integer, default=0)
    team_away_score = Column(Integer, default=0)
    status = Column(String, default="scheduled") # "scheduled", "live", "finished"
    match_date = Column(DateTime, nullable=True)

    # Магия SQLAlchemy: связи, чтобы получать полные данные о командах в матче
    home_team = relationship("TeamModel", foreign_keys=[team_home_id])
    away_team = relationship("TeamModel", foreign_keys=[team_away_id])
    tournament = relationship("TournamentModel", foreign_keys=[tournament_id])

class TournamentModel(Base):
    __tablename__ = "tournaments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    location = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)

    prize_pool = Column(BigInteger)
    region = Column(String)
    logo_url = Column(String, nullable=True) 

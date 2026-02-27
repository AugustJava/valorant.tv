from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class TeamModel(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    rank = Column(String)
    team = Column(String)
    country = Column(String)
    last_played = Column(String)
    last_played_team = Column(String)
    last_played_logo = Column(String)
    record = Column(String)
    earnings = Column(String)
    logo = Column(String)
    region = Column(String)

class NewsModel(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    date = Column(String)
    author = Column(String)
    url_path = Column(String)

class MatchModel(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    
    # Ссылки на ID команд
    team_home_id = Column(Integer, ForeignKey("teams.id"))
    team_away_id = Column(Integer, ForeignKey("teams.id"))
    
    score_home = Column(Integer, default=0)
    score_away = Column(Integer, default=0)
    status = Column(String)  # например: "upcoming", "live", "finished"
    date = Column(String)

    team_home = relationship("TeamModel", foreign_keys=[team_home_id])
    team_away = relationship("TeamModel", foreign_keys=[team_away_id])
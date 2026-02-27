from sqlalchemy import Column, Integer, String
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
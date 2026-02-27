from pydantic import BaseModel, Field
from typing import Optional, List

# Короткая инфо о команде для вкладывания в матчи
class TeamShort(BaseModel):
    id: int
    team: str
    logo: str
    country: str
    class Config:
        from_attributes = True

class TeamCreate(BaseModel):
    rank: str = Field(..., pattern=r"^\d+$")
    team: str = Field(..., min_length=2)
    country: str
    last_played: str
    last_played_team: str
    last_played_logo: str
    record: str = Field(..., pattern=r"^\d+-\d+$")
    earnings: str
    logo: str

class NewsCreate(BaseModel):
    title: str = Field(..., min_length=5)
    description: str
    date: str
    author: str
    url_path: str

class MatchCreate(BaseModel):
    team_home_id: int
    team_away_id: int
    score_home: int = 0
    score_away: int = 0
    status: str = "upcoming"
    date: str

class MatchRead(BaseModel):
    id: int
    score_home: int
    score_away: int
    status: str
    date: str
    team_home: TeamShort
    team_away: TeamShort
    class Config:
        from_attributes = True

class MatchUpdateStatus(BaseModel):
    status: str

class TeamStats(BaseModel):
    team_id: int
    team_name: str
    wins: int
    losses: int
    draws: int
    total_matches: int
    winrate: str

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    password: str # Обычный текст, который мы захешируем в main.py

class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool

    class Config:
        from_attributes = True
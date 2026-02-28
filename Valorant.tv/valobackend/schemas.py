from pydantic import BaseModel
from typing import Optional, List
import datetime

# --- Схемы Команд ---
class TeamBase(BaseModel):
    team: str
    region: str
    logo_url: Optional[str] = None
    is_active: bool = True

class TeamCreate(TeamBase):
    pass

class TeamResponse(TeamBase):
    id: int

    class Config:
        from_attributes = True # Для Pydantic V2 (или orm_mode = True, если у тебя старая версия)

class TeamStats(BaseModel):
    team_id: int
    team_name: str
    wins: int
    losses: int
    draws: int
    total_matches: int
    winrate: str

class MatchUpdateStatus(BaseModel):
    status: str # Например: "finished", "live"

# --- Схемы Матчей ---
class MatchBase(BaseModel):
    # Теперь при создании матча передаются только ID команд!
    team_home_id: int
    team_away_id: int
    team_home_score: int = 0
    team_away_score: int = 0
    status: str = "scheduled"
    match_date: Optional[datetime.datetime] = None

class MatchCreate(MatchBase):
    pass

class MatchResponse(MatchBase):
    id: int
    
    # Это самая крутая часть! В ответе матча будут вложены данные о командах
    home_team: TeamResponse 
    away_team: TeamResponse

    class Config:
        from_attributes = True

# --- Схемы Пользователей ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_admin: bool

    class Config:
        from_attributes = True

# --- Схемы Новостей ---
class NewsBase(BaseModel):
    title: str
    content: str

class NewsCreate(NewsBase):
    pass

class NewsResponse(NewsBase):
    id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True
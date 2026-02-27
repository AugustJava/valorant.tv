from pydantic import BaseModel
from typing import Optional

class NewsCreate(BaseModel):
    title: str
    description: str
    date: str
    author: str
    url_path: str

class TeamCreate(BaseModel):
    rank: str
    team: str
    country: str
    last_played: str
    last_played_team: str
    last_played_logo: str
    record: str
    earnings: str
    logo: str
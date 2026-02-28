from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas, database
from auth import get_current_user

# Создаем роутер. 
router = APIRouter(
    prefix="/tournaments", 
    tags=["Tournaments"]
)

@router.post("/", response_model=schemas.TournamentResponse)
def create_tournament(
    tournament: schemas.TournamentCreate,
    db: Session = Depends(database.get_db),
    current_user: models.UserModel = Depends(get_current_user)):

    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="У вас нет прав супер-админа")
    db_tournament = models.TournamentModel(**tournament.dict())
    db.add(db_tournament)
    db.commit()
    db.refresh(db_tournament)
    return db_tournament

@router.get("/", response_model=List[schemas.TournamentResponse])
def get_tournaments(db: Session = Depends(database.get_db)):
    db_t = db.query(models.TournamentModel).all()
    return db_t


# @app.get("/tournaments/{t_id}/leaderboard")
# def get_leaderboard(t_id: int, db: Session = Depends(database.get_db)):
#     # 1. Берем все завершенные матчи этого турнира
#     matches = db.query(models.MatchModel).filter(
#         models.MatchModel.tournament_id == t_id,
#         models.MatchModel.status == "finished"
#     ).all()

#     stats = {} # Тут будем хранить {team_id: {"wins": 0, "losses": 0}}

#     for m in matches:
#         # Инициализируем команды в словаре, если их там еще нет
#         for tid in [m.team_home_id, m.team_away_id]:
#             if tid not in stats:
#                 stats[tid] = {"wins": 0, "losses": 0}

#         # Считаем, кто победил
#         if m.team_home_score > m.team_away_score:
#             stats[m.team_home_id]["wins"] += 1
#             stats[m.team_away_id]["losses"] += 1
#         elif m.team_away_score > m.team_home_score:
#             stats[m.team_away_id]["wins"] += 1
#             stats[m.team_home_id]["losses"] += 1

#     return stats
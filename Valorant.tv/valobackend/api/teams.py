from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import or_
# Импортируем твои файлы (пути могут чуть отличаться в зависимости от твоей структуры)
import models, schemas, database
from auth import get_current_user

# Создаем роутер. 
# prefix="/teams" значит, что ко всем путям ниже автоматически добавится /teams
# tags=["Teams"] сгруппирует их в Swagger
router = APIRouter(
    prefix="/teams", 
    tags=["Teams"]
)

@router.get("/", response_model=List[schemas.TeamResponse])
def get_teams(region: str = None, db: Session = Depends(database.get_db)):
    query = db.query(models.TeamModel)
    if region:
        query = query.filter(models.TeamModel.region == region)
    return query.all()

@router.post("/", response_model=schemas.TeamResponse)
def post_team(team: schemas.TeamCreate, db: Session = Depends(database.get_db),
    current_user: models.UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="У вас нет прав супер-админа")
    db_team = models.TeamModel(**team.dict())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

@router.get("/{team_id}/stats", response_model=schemas.TeamStats)
def get_team_stats(team_id: int, db: Session = Depends(database.get_db)):
    team = db.query(models.TeamModel).filter(models.TeamModel.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Ищем завершенные матчи, где команда была либо домашней, либо гостевой
    matches = db.query(models.MatchModel).filter(
        models.MatchModel.status == "finished",
        or_(models.MatchModel.team_home_id == team_id, models.MatchModel.team_away_id == team_id)
    ).all()

    wins, losses, draws = 0, 0, 0

    for m in matches:
        # Поправленные названия полей: team_home_score и team_away_score
        if m.team_home_id == team_id:
            our, enemy = m.team_home_score, m.team_away_score
        else:
            our, enemy = m.team_away_score, m.team_home_score

        if our > enemy: wins += 1
        elif our < enemy: losses += 1
        else: draws += 1

    total = len(matches)
    winrate = f"{(wins / total * 100):.1f}%" if total > 0 else "0%"

    return {
        "team_id": team_id,
        "team_name": team.team,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "total_matches": total,
        "winrate": winrate
    }
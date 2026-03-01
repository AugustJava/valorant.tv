from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
# Импортируем твои файлы (пути могут чуть отличаться в зависимости от твоей структуры)
import models, schemas, database
from auth import get_current_user

# Создаем роутер. 
router = APIRouter(
    prefix="/matches", 
    tags=["Matches"]
)


@router.get("/")
def get_matches(status: str = None, tournament_id: int = None, db: Session = Depends(database.get_db)):
    query = db.query(models.MatchModel)
    if status:
        query = query.filter(models.MatchModel.status == status)
    if tournament_id:
        query = query.filter(models.MatchModel.tournament_id == tournament_id)
    return query.all()

@router.post("/", response_model=schemas.MatchResponse)
def create_match(match: schemas.MatchCreate, db: Session = Depends(database.get_db), current_user: models.UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="У вас нет прав супер-админа")
    
    tournament = db.query(models.TournamentModel).filter(models.TournamentModel.id==match.tournament_id).first()

    if not tournament:
        raise HTTPException(status_code=400, detail="Матч не входит в турниры")

    home_exists = db.query(models.TeamModel).filter(models.TeamModel.id == match.team_home_id).first()
    away_exists = db.query(models.TeamModel).filter(models.TeamModel.id == match.team_away_id).first()
    if not home_exists or not away_exists:
        raise HTTPException(status_code=404, detail="Одна или обе команды не найдены")
    if match.team_away_id == match.team_home_id:
        raise HTTPException(status_code=404, detail="Команда не может играть против самой себя")
    db_match = models.MatchModel(**match.dict())
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

@router.patch("/{match_id}/status")
def update_match_status(
    match_id: int, 
    status_data: schemas.MatchUpdateStatus, 
    db: Session = Depends(database.get_db)
):
    match = db.query(models.MatchModel).filter(models.MatchModel.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
        
    match.status = status_data.status 
    db.commit()
    db.refresh(match)
    return {"message": f"Match {match_id} status updated to {match.status}"}
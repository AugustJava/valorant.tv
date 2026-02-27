from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
import models, schemas, database
from sqlalchemy import or_
from passlib.context import CryptContext

# Настройка шифровальщика
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)



# Создаем таблицы
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/register", response_model=schemas.UserOut)
async def register_user(user_data: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # 1. Проверяем, есть ли уже такой пользователь
    existing_user = db.query(models.UserModel).filter(models.UserModel.username==user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
    
    # 2. Хешируем пароль
    hashed_pass = get_password_hash(user_data.password)
    # 3. Создаем запись в базе
    new_user = models.UserModel(
        username=user_data.username,
        hashed_password=hashed_pass,
        is_admin=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
# --- RANKINGS ---
@app.get("/rankings/{region}")
async def get_rankings(region: str, db: Session = Depends(database.get_db)):
    return db.query(models.TeamModel).filter(models.TeamModel.region == region).all()

@app.post("/rankings/{region}")
async def create_team(region: str, team: schemas.TeamCreate, db: Session = Depends(database.get_db)):
    db_team = models.TeamModel(**team.dict(), region=region)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

@app.delete("/rankings/{team_id}")
async def delete_team(team_id: int, db: Session = Depends(database.get_db)):
    team = db.query(models.TeamModel).filter(models.TeamModel.id == team_id).first()
    if not team: raise HTTPException(status_code=404, detail="Team not found")
    db.delete(team)
    db.commit()
    return {"message": "Deleted"}

# @app.get("/teams/{team_id}/stats", response_model=)

# --- NEWS ---
@app.get("/news")
async def get_news(db: Session = Depends(database.get_db)):
    return db.query(models.NewsModel).all()

@app.post("/news")
async def create_news(news: schemas.NewsCreate, db: Session = Depends(database.get_db)):
    db_news = models.NewsModel(**news.dict())
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news

# --- MATCHES ---
@app.get("/matches", response_model=list[schemas.MatchRead])
async def get_matches(db: Session = Depends(database.get_db)):
    return db.query(models.MatchModel).options(
        joinedload(models.MatchModel.team_home),
        joinedload(models.MatchModel.team_away)
    ).all()

@app.get("/matches/team/{team_id}", response_model=list[schemas.MatchRead])
async def get_matches_of_team(team_id: int, db: Session = Depends(database.get_db)):
    matches = db.query(models.MatchModel).options(
        joinedload(models.MatchModel.team_home),
        joinedload(models.MatchModel.team_away)
    ).filter(
        or_(models.MatchModel.team_home_id== team_id, models.MatchModel.team_away_id==team_id)
    ).all()
    

    if not matches:
        return []
    return matches

@app.post("/matches", response_model=schemas.MatchRead)
async def create_match(match: schemas.MatchCreate, db: Session = Depends(database.get_db)):
    db_match = models.MatchModel(**match.dict())
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match


@app.patch("/matches/{match_id}/status")
async def update_match_status(
    match_id: int, # Берем ID из URL (например, /matches/5/status)
    status_data: schemas.MatchUpdateStatus, # Берем новый статус из тела JSON
    db: Session = Depends(database.get_db) # Тут скобки не нужны
):
    # Ищем матч
    match = db.query(models.MatchModel).filter(models.MatchModel.id == match_id).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
        
    # Меняем старый статус на новый из нашей схемы
    match.status = status_data.status 
    
    db.commit()
    db.refresh(match)
    
    # Возвращаем сообщение об успехе
    return {"message": f"Match {match_id} status updated to {match.status}"}


from sqlalchemy import or_

@app.get("/teams/{team_id}/stats", response_model=schemas.TeamStats)
async def get_team_stats(team_id: int, db: Session = Depends(database.get_db)):
    # 1. Сначала проверим, существует ли такая команда
    team = db.query(models.TeamModel).filter(models.TeamModel.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # 2. Достаем все ЗАВЕРШЕННЫЕ матчи этой команды
    matches = db.query(models.MatchModel).filter(
        models.MatchModel.status == "finished",
        or_(models.MatchModel.team_home_id == team_id, models.MatchModel.team_away_id == team_id)
    ).all()

    # 3. Инициализируем счетчики
    wins = 0
    losses = 0
    draws = 0

    # 4. Считаем результат каждого матча
    for match in matches:
        # Определяем, был ли это домашний матч или гостевой
        if match.team_home_id == team_id:
            our_score = match.score_home
            enemy_score = match.score_away
        else:
            our_score = match.score_away
            enemy_score = match.score_home

        # Сравниваем счета
        if our_score > enemy_score:
            wins += 1
        elif our_score < enemy_score:
            losses += 1
        else:
            draws += 1

    # 5. Считаем винрейт
    total = len(matches)
    winrate_percent = "0%"
    if total > 0:
        winrate_percent = f"{(wins / total) * 100:.1f}%"

    # 6. Собираем всё в ответ
    return {
        "team_id": team_id,
        "team_name": team.team,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "total_matches": total,
        "winrate": winrate_percent
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
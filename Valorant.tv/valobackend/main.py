from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
import models, schemas, database

# Создаем таблицы
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

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

@app.post("/matches", response_model=schemas.MatchRead)
async def create_match(match: schemas.MatchCreate, db: Session = Depends(database.get_db)):
    db_match = models.MatchModel(**match.dict())
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
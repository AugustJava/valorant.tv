import os
import json 
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import models, database, schemas
from sqlalchemy.orm import Session

app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ЭТО ВАЖНО: Разрешаем фронтенду подключаться к нам
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # В будущем заменим на адрес сайта друга
    allow_methods=["*"],
    allow_headers=["*"]
)

def load_json(filename: str):
    with open(f"data/{filename}", "r", encoding="utf-8") as f:
        return json.load(f)
    
@app.get("/news")
async def get_news(news: schemas.NewsCreate):
    data = load_json("news.json")
    return data

@app.get("/rankings/{region}")
async def get_rankings(region: str, db: Session = Depends(get_db)):
    teams = db.query(models.TeamModel).filter(models.TeamModel.region == region).all()
    return teams

@app.post("/news")
async def create_news(news: schemas.NewsCreate):
    # 1. Читаем текущий список новостей
    data = load_json("news.json")

    # 2. Превращаем присланную новость в словарь и добавляем в список
    # (у тебя в JSON новости лежат в ключе "segments")
    new_post = news.dict()
    data["data"]["segments"].append(new_post)

    # 3. Сохраняем обновленный список обратно в файл
    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return {"Message": "News added succesfully", "news": new_post}

@app.post("/rankings/{region}")
async def create_team(region: str, team: schemas.TeamCreate, db: Session = Depends(get_db)):
    # 1. Создаем объект модели из того, что прислал юзер
    db_team = models.TeamModel(
        **team.dict(), # "Распаковываем" все поля (rank, team и т.д.)
        region=region  # Добавляем регион отдельно
    )
    
    # 2. Сохраняем в базу
    db.add(db_team)
    db.commit() # Подтверждаем сохранение
    db.refresh(db_team) # Обновляем объект, чтобы получить ID, который база дала сама
    
    return db_team

@app.delete("/rankings/{team_id}")
async def delete_team(team_id: int, db: Session = Depends(get_db)):
    # Ищем команду в базе по ID
    team = db.query(models.TeamModel).filter(models.TeamModel.id == team_id).first()
    
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    db.delete(team)
    db.commit()
    
    return {"message": f"Team with ID {team_id} deleted"}

@app.patch("/rankings/{team_id}")
async def update_rank(team_id: int, new_rank: str, db: Session = Depends(get_db)):
    team = db.query(models.TeamModel).filter(models.TeamModel.id == team_id).first()
    

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    team.rank = new_rank
    db.commit()
    db.refresh()
    return {"message": f"Rank for team {team.team} (ID: {team_id}) updated to {new_rank}"}


if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, database
from auth import get_current_user
from typing import List

router = APIRouter(prefix="/news", tags=["News"])

@router.get("/", response_model=List[schemas.NewsResponse])
def get_news(db: Session = Depends(database.get_db)):
    return db.query(models.NewsModel).all()

@router.post("/", response_model=schemas.NewsResponse)
async def create_news(news: schemas.NewsCreate, db: Session = Depends(database.get_db),
    current_user : models.UserModel = Depends(get_current_user)):
    # Проверяем флаг в базе данных
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="У вас нет прав супер-админа")
    db_news = models.NewsModel(**news.dict())
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news
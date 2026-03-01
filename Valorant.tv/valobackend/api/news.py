from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, database
from auth import get_current_user
from typing import List

router = APIRouter(prefix="/news", tags=["News"])

@router.get("/", response_model=List[schemas.NewsResponse])
def get_news(db: Session = Depends(database.get_db)):
    return db.query(models.NewsModel).order_by(models.NewsModel.created_at.desc()).all()

@router.get("/{news_id}", response_model=schemas.NewsResponse)
def get_news_article(news_id: int, db: Session = Depends(database.get_db)):
    aritcle = db.query(models.NewsModel).filter(models.NewsModel.id==news_id).first()
    if not aritcle:
        raise HTTPException(status_code=404, detail="News not found")
    return aritcle

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
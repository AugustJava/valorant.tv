from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import models, schemas, database, auth # Импортируем наш новый auth.py

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Проверка, есть ли такой юзер
    db_user = db.query(models.UserModel).filter(models.UserModel.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="username already registered")
    
    # Хешируем пароль через функцию из auth.py
    hashed_pwd = auth.get_password_hash(user.password)
    
    new_user = models.UserModel(username=user.username, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    # 1. Ищем юзера
    user = db.query(models.UserModel).filter(models.UserModel.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # 2. Создаем токен (функция из auth.py)
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
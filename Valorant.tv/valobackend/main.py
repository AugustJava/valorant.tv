from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload
import models, schemas, database
from sqlalchemy import or_
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError



# Настройка шифровальщика
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)


SECRET_KEY = "SUPER_SECRET_VALORANT_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

oauth_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code= 401,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        # 1. Расшифровываем токен своим SECRET_KEY
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        # Если токен подделан или просрочен — вылетает ошибка
        raise credentials_exception
    # 2. Ищем пользователя в базе
    user = db.query(models.UserModel).filter(models.UserModel.username==username).first()
    if user is None:
        raise credentials_exception
    return user # Если всё ок, возвращаем объект пользователя

# Создаем таблицы
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/register", response_model=schemas.UserResponse)
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

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.UserModel).filter(models.UserModel.username==form_data.username).first()

    # 2. Проверяем существование и пароль
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный логин или пароль")
    
    # 3. Создаем токен
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}






# --- NEWS ---
@app.get("/news", response_model=list[schemas.NewsResponse])
async def get_news(db: Session = Depends(database.get_db)):
    return db.query(models.NewsModel).all()

@app.post("/news", response_model=list[schemas.NewsResponse])
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

# --- МАТЧИ ---

@app.get("/matches", response_model=list[schemas.MatchResponse])
def get_matches(db: Session = Depends(database.get_db)):
    # Благодаря relationship в моделях, подгрузка команд произойдет автоматически
    return db.query(models.MatchModel).all()

@app.patch("/matches/{match_id}/status")
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

# --- СТАТИСТИКА КОМАНД ---



@app.get("/teams/{team_id}/stats", response_model=schemas.TeamStats)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
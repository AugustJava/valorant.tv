from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import teams, matches, tournaments, users, news # Добавили users
import models, database

# Создаем таблицы
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Valorant TV API")

# Подключаем все роутеры
app.include_router(users.router)
app.include_router(teams.router)
app.include_router(matches.router)
app.include_router(tournaments.router)
app.include_router(news.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)











if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
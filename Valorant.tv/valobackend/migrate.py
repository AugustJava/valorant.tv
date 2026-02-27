import json
import os
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

db = SessionLocal()

def migrate_rankings():
    # Список регионов, которые у тебя есть в файлах
    regions = ["eu", "na", "ap", "la", "br", "kr", "jp"]
    
    for region in regions:
        filename = f"data/rankings-{region}.json"
        
        if os.path.exists(filename):
            print(f"Обработка региона: {region}...")
            with open(filename, "r", encoding="utf-8") as f:
                content = json.load(f)
                teams_list = content.get("data", [])
                
                for team_data in teams_list:
                    # Создаем объект модели для базы данных
                    # Мы добавляем поле region вручную, так как в JSON его нет
                    db_team = models.TeamModel(
                        rank=team_data.get("rank"),
                        team=team_data.get("team"),
                        country=team_data.get("country"),
                        last_played=team_data.get("last_played"),
                        last_played_team=team_data.get("last_played_team"),
                        last_played_logo=team_data.get("last_played_logo"),
                        record=team_data.get("record"),
                        earnings=team_data.get("earnings"),
                        logo=team_data.get("logo"),
                        region=region
                    )
                    db.add(db_team)
            
            print(f"Регион {region} готов!")
    
    db.commit()
    print("Миграция завершена успешно!")

if __name__ == "__main__":
    # Сначала убедимся, что таблицы созданы
    models.Base.metadata.create_all(bind=engine)
    migrate_rankings()
    db.close()
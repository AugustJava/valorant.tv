import React, { useEffect, useState } from "react"; // Добавляем хуки
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "../styles/pages/News.scss";

interface TeamsItem {
  id: number;
  team: string;
  region: string;
  logo_url: string; // В JSON даты приходят строками
  is_active: boolean;
}

const Teams = () => {
  // 2. Создаем "состояние" (State) для хранения новостей
  // По умолчанию это пустой массив []. TS поймет, что там будут объекты типа NewsItem
  const [teams, setTeams] = useState<TeamsItem[]>([]);
  
  // Состояние для индикатора загрузки (чтобы юзер не видел пустой экран)
  const [isLoading, setIsLoading] = useState(true);

  // 3. Хук useEffect — "сердце" связи с бэкендом
  useEffect(() => {
    // Эта функция сработает один раз при открытии страницы
    const fetchTeams = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/teams");
        const data = await response.json();
        setTeams(data); // Сохраняем полученные новости в состояние
      } catch (error) {
        console.error("Ошибка при загрузке новостей:", error);
      } finally {
        setIsLoading(false); // Выключаем спиннер/индикатор загрузки
      }
    };

    fetchTeams();
  }, []); // Пустой массив зависимостей = запуск 1 раз

  return (
    <div>
      <Navbar />
      <div className="Teams-page">
        <h1>Teams</h1>

        {/* 4. Проверка состояния загрузки */}
        {isLoading ? (
          <p>Loading teams from database...</p>
        ) : (
          /* 5. Рендерим список из состояния news */
          teams.map((item) => (
            <div key={item.id} className="news-item">
              <h2>{item.team}</h2>
                    <div className="team-card">
      {/* Исправлено: используем item вместо teams */}
      {item.logo_url ? (
        <img 
          src={item.logo_url} 
          alt={`${item.team} logo`} 
          style={{ width: "50px", height: "50px", objectFit: "contain" }} 
        />
      ) : (
        <div className="no-logo">?</div>
      )}
    </div>
              <p>{item.region}</p>
              <p>
              <strong>Currently:</strong> {item.is_active ? "Active" : "Inactive"}
              </p>
              <button className="read-more-btn">Read more</button>
            </div>
          ))
        )}
      </div>
      <Footer />
    </div>
  );
};


export default Teams;
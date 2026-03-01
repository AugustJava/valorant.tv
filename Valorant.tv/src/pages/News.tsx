import React, { useEffect, useState } from "react"; // Добавляем хуки
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "../styles/pages/News.scss";
import { Link } from "react-router";

// 1. Описываем структуру новости, которая приходит из FastAPI (модель NewsResponse)
interface NewsItem {
  id: number;
  title: string;
  content: string;
  created_at: string; // В JSON даты приходят строками
}

const News = () => {
  // 2. Создаем "состояние" (State) для хранения новостей
  // По умолчанию это пустой массив []. TS поймет, что там будут объекты типа NewsItem
  const [news, setNews] = useState<NewsItem[]>([]);
  
  // Состояние для индикатора загрузки (чтобы юзер не видел пустой экран)
  const [isLoading, setIsLoading] = useState(true);

  // 3. Хук useEffect — "сердце" связи с бэкендом
  useEffect(() => {
    // Эта функция сработает один раз при открытии страницы
    const fetchNews = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/news");
        const data = await response.json();
        setNews(data); // Сохраняем полученные новости в состояние
      } catch (error) {
        console.error("Ошибка при загрузке новостей:", error);
      } finally {
        setIsLoading(false); // Выключаем спиннер/индикатор загрузки
      }
    };

    fetchNews();
  }, []); // Пустой массив зависимостей = запуск 1 раз

  return (
    <div>
      <Navbar />
      <div className="news-page">
        <h1>Latest News</h1>

        {/* 4. Проверка состояния загрузки */}
        {isLoading ? (
          <p>Loading news from database...</p>
        ) : (
          /* 5. Рендерим список из состояния news */
          news.map((item) => (
            <div key={item.id} className="news-item">
              <h2>{item.title}</h2>
              {/* <p>{item.summary}</p> */}
              <p>
                <strong>Date:</strong> {new Date(item.created_at).toLocaleDateString()}
              </p>
              <Link to={`/news/${item.id}`} className="read-more-btn">
              Read more
              </Link>
            </div>
          ))
        )}
      </div>
      <Footer />
    </div>
  );
};

export default News;
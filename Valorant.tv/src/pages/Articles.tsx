import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router'; // Чтобы достать ID из ссылки
import parse from 'html-react-parser'; // Чтобы превратить строку в живой HTML
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

interface News {
  id: number;
  title: string;
  content: string;
  author: string;
  image_url: string;
  created_at: string;
}

const Article = () => {
  const { id } = useParams(); // Достаем ID из URL (например, /news/1)
  const [article, setArticle] = useState<News | null>(null);

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/news/${id}`)
      .then(res => res.json())
      .then(data => setArticle(data))
      .catch(err => console.error("Error loading article:", err));
  }, [id]);

  if (!article) return <div style={{color: 'white'}}>Loading...</div>;

  return (
    <div style={{ backgroundColor: '#0f1923', minHeight: '100vh', color: 'white' }}>
      <Navbar />
      <div style={containerStyle}>
        <img src={article.image_url} alt={article.title} style={mainImageStyle} />
        <h1 style={titleStyle}>{article.title}</h1>
        <div style={metaStyle}>By {article.author} • {new Date(article.created_at).toLocaleDateString()}</div>
        
        {/* САМОЕ ВАЖНОЕ: Рендерим HTML из базы */}
        <div className="article-content" style={contentStyle}>
          {parse(article.content)}
        </div>
      </div>
      <Footer />
    </div>
  );
};

// Простые стили для примера
const containerStyle = { maxWidth: '800px', margin: '40px auto', padding: '0 20px' };
const mainImageStyle = { width: '100%', borderRadius: '8px', marginBottom: '20px' };
const titleStyle = { fontSize: '36px', marginBottom: '10px' };
const metaStyle = { color: '#888', marginBottom: '30px', borderBottom: '1px solid #333', paddingBottom: '10px' };
const contentStyle = { lineHeight: '1.6', fontSize: '18px' };

export default Article;
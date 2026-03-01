import React, {useState, useEffect} from 'react'


interface Tournament {
    id: number;
    name: string;
    start_date: string;
    end_date: string;
    location: string;
    prize_pool: number;
    logo_url: string;
}

const TournamentBanner = () => {
    const [tournaments, setTournaments] = useState<Tournament[]>([]);
    useEffect(() =>{
        fetch('http://127.0.0.1:8000/tournaments/')
        .then(res => res.json())
        .then(data => setTournaments(data))
        .catch(err => console.error("Backend offline?", err));
    }, []);

    if (tournaments.length === 0) return null;

    const t = tournaments[0]

    return (
        <div className="tournament-banner" style={bannerStyle}>
            <div className="banner-content" style={{display: 'flex', alignItems: 'center', gap: '20px' }}>
                {t.logo_url && (
                    <img src={t.logo_url} alt="Tournament Logo" 
                    style={{ width: '80px', height: '80px', objectFit: 'contain' }} />
                )}
                <span style={dateTag}>{new Date(t.start_date).toLocaleDateString('en-US', {month:'short', day:'numeric'})}</span>
                <h1>{t.name}</h1>
                <p>Location: {t.location} | Prize: ${t.prize_pool.toLocaleString()}</p>
            </div>
        </div>
    );
};

const bannerStyle: React.CSSProperties = {
  background: 'linear-gradient(90deg, #ff4655 0%, #0f1923 100%)',
  padding: '40px',
  color: 'white',
  marginBottom: '30px',
  borderRadius: '4px'
};

const dateTag: React.CSSProperties = {
  background: 'white',
  color: '#ff4655',
  padding: '4px 8px',
  fontWeight: 'bold',
  fontSize: '12px'
};  
export default TournamentBanner;
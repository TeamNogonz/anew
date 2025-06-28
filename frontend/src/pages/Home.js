import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import ApiService from '../api/services';
import './Home.css';

const Home = () => {
  const [pingResult, setPingResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePingTest = async () => {
    setLoading(true);
    setError(null);
    setPingResult(null);

    try {
      const result = await ApiService.ping();
      setPingResult(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home">
      <header className="home-header">
        <h1>뉴스 요약 서비스</h1>
        <p>AI를 활용한 뉴스 요약 및 분석</p>
      </header>

      <main className="home-main">
        <section className="ping-section">
          <h2>서버 연결 테스트</h2>
          <button 
            onClick={handlePingTest} 
            disabled={loading}
            className="ping-button"
          >
            {loading ? '테스트 중...' : 'Ping 테스트'}
          </button>

          {pingResult && (
            <div className="ping-result success">
              <h3>✅ 서버 연결 성공!</h3>
              <pre>{JSON.stringify(pingResult, null, 2)}</pre>
            </div>
          )}

          {error && (
            <div className="ping-result error">
              <h3>❌ 서버 연결 실패</h3>
              <p>{error}</p>
            </div>
          )}
        </section>

        <section className="features">
          <h2>주요 기능</h2>
          <div className="feature-grid">
            <div className="feature-card">
              <h3>📰 뉴스 요약</h3>
              <p>긴 뉴스 기사를 AI가 핵심 내용으로 요약</p>
            </div>
            <div className="feature-card">
              <h3>🔍 키워드 추출</h3>
              <p>뉴스에서 중요한 키워드와 주제를 자동 추출</p>
            </div>
            <div className="feature-card">
              <h3>📊 분석 리포트</h3>
              <p>뉴스 내용을 바탕으로 한 인사이트 분석</p>
            </div>
          </div>
        </section>

        <nav className="navigation">
          <Link to="/about" className="nav-link">서비스 소개</Link>
        </nav>
      </main>
    </div>
  );
};

export default Home; 
import React, { useEffect, useState } from 'react';
import styles from './Home.module.css';
import NewsBox from './NewsBox';
import TopicCardSet from './TopicCardSet';
import Footer from './Footer';
import ApiService from '../api/services';

const newsList = '매일경제 · 한국경제 · 서울경제 · 머니투데이 · 이데일리 · 비즈워치';

const Home = () => {
  const [summary, setSummary] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    ApiService.getNewsData()
      .then(res => {
        setSummary(res.summary || res);
        setLoading(false);
      })
      .catch(err => {
        setError('데이터를 불러오지 못했습니다.');
        setLoading(false);
      });
  }, []);

  if (loading) return <div className={styles['main-container']}>로딩 중...</div>;
  if (error) return <div className={styles['main-container']}>{error}</div>;

  // summary가 빈 배열이거나 빈 객체일 때 안내 문구 출력
  const isEmpty =
    (Array.isArray(summary) && summary.length === 0) ||
    (typeof summary === 'object' && summary !== null && Object.keys(summary).length === 0);

  return (
    <>
      <div className={styles.intro}>
        Anew는 다양한 시각의 AI 요약으로, 편향 없이 핵심만 전달하는 시사 뉴스 요약 서비스입니다 ☺️
      </div>
      <div className={styles['main-container']}>
        <h1 className={styles.title}>
          <img className={styles.logo} src={process.env.PUBLIC_URL + '/Anew_logo.png'} alt="Anew 로고" />
          Anew
        </h1>
        {isEmpty ? (
          <div style={{ textAlign: 'center', padding: '4rem 1rem', color: '#64748b', fontSize: '1.2rem', fontWeight: 500 }}>
            <div style={{ fontSize: '2.2rem', marginBottom: '1.2rem' }}>📰</div>
            아직 AI로 요약된 뉴스가 없어요.<br />
            조금만 기다려주세요!
          </div>
        ) : (
          <>
            <NewsBox subtitle="Ai 뉴스 요약에 활용된 언론사" newsList={newsList} />
            <div className={styles['update-time']}>업데이트 시간: 2025.06.20, 13:00</div>
            {summary.map((item, idx) => (
              <TopicCardSet
                key={idx}
                title={item.title}
                first={item.first_perspective}
                second={item.second_perspective}
                reference_url={item.reference_url}
              />
            ))}
          </>
        )}
      </div>
      <Footer />
    </>
  );
};

export default Home; 
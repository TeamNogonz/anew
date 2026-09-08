import React, { useEffect, useState } from 'react';
import styles from './Home.module.css';
import NewsBox from './NewsBox';
import TopicCardSet from './TopicCardSet';
import Footer from './Footer';
import ApiService from '../api/services';
import AnewLogo from '../assets/Anew_logo.png';

const newsList = '매일경제 · 한국경제 · 서울경제 · 머니투데이 · 이데일리 · 비즈워치';

const Home = () => {
  const [summary, setSummary] = useState([]);
  const [createdAt, setCreatedAt] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 날짜 포맷팅 함수
  const formatUpdateTime = (dateString) => {
    if (!dateString) return '';
    
    try {
      const date = new Date(dateString);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      
      return `${year}.${month}.${day}, ${hours}:${minutes}`;
    } catch (error) {
      console.error('날짜 포맷팅 오류:', error);
      return '';
    }
  };

  useEffect(() => {
    ApiService.getNewsData()
      .then(res => {
        // 기존 응답 구조와 새로운 응답 구조 모두 지원
        if (res.summary_items) {
          setSummary(res.summary_items);
          setCreatedAt(res.created_at);
        } else if (Array.isArray(res)) {
          setSummary(res);
          setCreatedAt(null);
        } else {
          setSummary(Array.isArray(res.summary) ? res.summary : []);
          setCreatedAt(null);
        }
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
        Anew는 주요 뉴스를 서로 다른 관점으로 요약합니다. 원문과 함께 살펴보세요.
      </div>
      <div className={styles['main-container']}>
        <h1 className={styles.title}>
          <img className={styles.logo} src={AnewLogo} alt="Anew 로고" />
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
            {createdAt && (
              <div className={styles['update-time']}>
                업데이트 시간: {formatUpdateTime(createdAt)}
              </div>
            )}
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

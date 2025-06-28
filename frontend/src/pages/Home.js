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
    const newsData = {}; // 필요시 실제 데이터로 교체
    ApiService.summarizeNews(newsData)
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
      </div>
      <Footer />
    </>
  );
};

export default Home; 
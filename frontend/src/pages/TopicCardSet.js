import React from 'react';
import styles from './Home.module.css';
import PerspectiveCard from './PerspectiveCard';

const TopicCardSet = ({ title, first, second, reference_url }) => (
  <>
    <div className={styles['topic-title']}>{title}</div>
    <div className={styles['card-row']}>
      <PerspectiveCard {...first} type="first" />
      <PerspectiveCard {...second} type="second" />
    </div>
    {reference_url && reference_url.length > 0 && (
      <div className={styles.card} style={{ maxWidth: 600, margin: '0.5rem auto 1.5rem auto', background: '#f8fafc', display: 'flex', flexDirection: 'column', justifyContent: 'flex-start' }}>
        <div className={styles['card-links-title']} style={{ marginTop: 0, marginBottom: '0.5rem' }}>요약에 활용된 뉴스</div>
        <div className={styles['card-links']} style={{ marginTop: 0 }}>
          {reference_url.map((url, idx) => (
            <a key={idx} href={url} target="_blank" rel="noopener noreferrer">{url}</a>
          ))}
        </div>
      </div>
    )}
  </>
);

export default TopicCardSet; 
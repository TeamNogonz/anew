import React from 'react';
import styles from './Home.module.css';

const PerspectiveCard = ({ type, title, icon, perspectives, links }) => (
  <div className={type === 'negative' ? `${styles.card} ${styles.negative}` : styles.card}>
    <div className={styles['card-title']}>
      <span className={styles.icon}>{icon}</span>
      {title}
    </div>
    <ul>
      {perspectives.map((item, idx) => <li key={idx}>{item}</li>)}
    </ul>
    <div className={type === 'negative' ? `${styles['card-links']} ${styles.negative}` : styles['card-links']}>
      <div className={styles['card-links-title']}>요약에 활용된 뉴스</div>
      {links.map((url, idx) => (
        <a key={idx} href={url} target="_blank" rel="noopener noreferrer">{url}</a>
      ))}
    </div>
  </div>
);

export default PerspectiveCard; 
import React from 'react';
import styles from './Home.module.css';

const PerspectiveCard = ({ type, title, icon, perspectives }) => (
  <div className={type === 'second' ? `${styles.card} ${styles.negative}` : `${styles.card} ${styles.positive}`}>
    <div className={styles['card-title']}>
      <span className={styles.icon}>{icon}</span>
      {title}
    </div>
    <ul>
      {perspectives.map((item, idx) => <li key={idx}>{item}</li>)}
    </ul>
  </div>
);

export default PerspectiveCard; 
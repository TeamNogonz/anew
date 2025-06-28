import React from 'react';
import styles from './Home.module.css';

const NewsBox = ({ subtitle, newsList }) => (
  <div className={styles['news-box']}>
    <div className={styles.subtitle}>{subtitle}</div>
    <div className={styles['news-list']}>{newsList}</div>
  </div>
);

export default NewsBox; 
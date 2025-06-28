import React from 'react';
import styles from './Home.module.css';
import PerspectiveCard from './PerspectiveCard';

const TopicCardSet = ({ title, first, second }) => (
  <>
    <div className={styles['topic-title']}>{title}</div>
    <div className={styles['card-row']}>
      <PerspectiveCard {...first} />
      <PerspectiveCard {...second} />
    </div>
  </>
);

export default TopicCardSet; 
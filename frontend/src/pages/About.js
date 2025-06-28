import React from 'react';
import { Link } from 'react-router-dom';
import './About.css';

const About = () => {
  return (
    <div className="about">
      <header className="about-header">
        <h1>서비스 소개</h1>
        <Link to="/" className="back-link">← 홈으로 돌아가기</Link>
      </header>

      <main className="about-main">
        <section className="about-content">
          <h2>뉴스 요약 서비스란?</h2>
          <p>
            이 서비스는 AI 기술을 활용하여 긴 뉴스 기사를 읽기 쉬운 요약본으로 변환해주는 
            웹 애플리케이션입니다. 바쁜 현대인들이 핵심 정보를 빠르게 파악할 수 있도록 
            도와줍니다.
          </p>

          <h3>주요 특징</h3>
          <ul>
            <li>🤖 <strong>AI 기반 요약:</strong> Google AI 기술을 활용한 정확한 요약</li>
            <li>⚡ <strong>빠른 처리:</strong> 실시간으로 뉴스 내용을 분석하고 요약</li>
            <li>📱 <strong>반응형 디자인:</strong> 모든 기기에서 편리하게 사용</li>
            <li>🔒 <strong>안전한 처리:</strong> 개인정보 보호 및 보안 강화</li>
          </ul>

          <h3>기술 스택</h3>
          <div className="tech-stack">
            <div className="tech-item">
              <h4>Backend</h4>
              <ul>
                <li>Python FastAPI</li>
                <li>Google AI API</li>
                <li>MongoDB</li>
              </ul>
            </div>
            <div className="tech-item">
              <h4>Frontend</h4>
              <ul>
                <li>React 19</li>
                <li>React Router</li>
                <li>Axios</li>
              </ul>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default About; 
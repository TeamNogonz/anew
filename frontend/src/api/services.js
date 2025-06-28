import api from './axios';

// API 서비스 클래스
export class ApiService {
  // 서버 상태 확인 (ping)
  static async ping() {
    try {
      const response = await api.get('/api/ping');
      return response.data;
    } catch (error) {
      throw new Error(`서버 연결 실패: ${error.message}`);
    }
  }

  // 뉴스 요약 API (향후 사용을 위한 예시)
  static async summarizeNews(newsData) {
    try {
      const response = await api.get('/data', newsData);
      return response.data;
    } catch (error) {
      throw new Error(`뉴스 요약 실패: ${error.message}`);
    }
  }
}

export default ApiService; 
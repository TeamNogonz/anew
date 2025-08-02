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


  static async getNewsData() {
    try {
      const response = await api.get('/api/data');
      return response.data;
    } catch (error) {
      throw new Error(`뉴스 데이터 조회 실패: ${error.message}`);
    }
  }
}

export default ApiService; 
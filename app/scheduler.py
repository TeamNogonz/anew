import schedule
import time
from crawl import getNewsUrlByMediaId, getNews, mediaIdList
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from anew_service import anew_service
from database import mongodb
from logger import get_logger

logger = get_logger()

MAX_NEWS_BY_MEDIA = 2  # 언론사 별, 가져올 최대 뉴스 개수

class NewsScheduler:
    def __init__(self):
        self.driver = None
        self.is_running = False
        
    def setup_driver(self):
        """Chrome WebDriver 설정"""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), 
                options=options
            )
            logger.info("Chrome WebDriver 설정 완료")
        except Exception as e:
            logger.error(f"WebDriver 설정 실패: {e}")
            raise
    
    def cleanup_driver(self):
        """WebDriver 정리"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Chrome WebDriver 정리 완료")
            except Exception as e:
                logger.error(f"WebDriver 정리 실패: {e}")
    
    def crawl_news(self):
        """뉴스 크롤링 수행"""
        try:
            start_time = time.time()
            logger.info(f"[Crawl] Start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")

            
            if not self.driver:
                self.setup_driver()
            
            mediaIds = list(mediaIdList.keys())
            newsData = {mediaIdList[mediaId]: [] for mediaId in mediaIds}
            
            # 언론사별 실패 카운트 초기화
            fail_counts = {mediaIdList[mediaId]: 0 for mediaId in mediaIds}
            
            for mediaId in mediaIds:
                mediaName = mediaIdList[mediaId]
                collected = newsData[mediaName]
                
                try:
                    urls = getNewsUrlByMediaId(self.driver, mediaId)
                    
                    for url in urls:
                        if len(collected) >= MAX_NEWS_BY_MEDIA:
                            break
                        if any(d['url'] == url for d in collected):
                            continue
                        
                        details = getNews(self.driver, url)
                        if details:
                            collected.append({
                                "press": mediaName,
                                "url": url,
                                **details
                            })
                        else:
                            fail_counts[mediaName] += 1
                            logger.warning(f"[Crawl] '{mediaName}' 상세페이지 추출 실패: {url}")
                    
                    logger.info(f"[Crawl] {mediaName}: {len(collected)}개 뉴스 수집 완료")
                    
                except Exception as e:
                    logger.error(f"[Crawl] {mediaName} 크롤링 중 오류: {e}")
                    continue
            
            # 수집된 뉴스 데이터를 하나의 리스트로 합치기
            all_news = []
            for press, news_list in newsData.items():
                all_news.extend(news_list)
            
            if all_news:
                logger.info(f"[Crawl] 총 {len(all_news)}개 뉴스 수집 완료")
                
                # 뉴스 요약 및 저장
                try:
                    anew_service.process_and_save_summary(all_news)
                    logger.info("[Crawl] 뉴스 요약 및 저장 완료")
                except Exception as e:
                    logger.error(f"[Crawl] 뉴스 요약 및 저장 실패: {e}")
            else:
                logger.warning("[Crawl] 수집된 뉴스가 없습니다")
            
            end_time = time.time()
            elapsed = end_time - start_time
            logger.info(f"[Crawl] End time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
            logger.info(f"[Crawl] Elapsed time: {elapsed:.4f} seconds")
        except Exception as e:
            logger.error(f"[Crawl] 크롤링 작업 중 오류 발생: {e}")
        finally:
            # WebDriver는 유지 (재사용을 위해)
            pass
    
    def start_scheduler(self, hour_interval: int = 6):
        """스케줄러 시작"""
        try:
            from config import settings
            
            # 설정에서 간격 가져오기 (파라미터보다 설정 우선)
            interval = settings.schedule_interval if hasattr(settings, 'schedule_interval') else hour_interval
            
            logger.info(f"[Scheduler] 뉴스 스케줄러 시작 - {interval}시간 간격")
            
            # WebDriver 설정
            self.setup_driver()
            
            # 스케줄 설정
            schedule.every(interval).hours.do(self.crawl_news)
            
            # 즉시 첫 번째 실행
            logger.info("[Scheduler] 첫 번째 크롤링 작업 시작")
            self.crawl_news()
            
            self.is_running = True
            
            # 스케줄러 루프
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 스케줄 확인
                
        except KeyboardInterrupt:
            logger.info("[Scheduler] 스케줄러 중단 요청 받음")
        except Exception as e:
            logger.error(f"[Scheduler] 스케줄러 실행 중 오류: {e}")
        finally:
            self.stop_scheduler()
    
    def stop_scheduler(self):
        """스케줄러 중지"""
        logger.info("[Scheduler] 스케줄러 중지")
        self.is_running = False
        self.cleanup_driver()
    
    def run_once(self):
        """한 번만 실행 (테스트용)"""
        try:
            logger.info("단일 크롤링 작업 시작")
            mongodb.connect()
            self.setup_driver()
            self.crawl_news()
        except Exception as e:
            logger.error(f"단일 크롤링 작업 실패: {e}")
        finally:
            self.cleanup_driver()
            mongodb.disconnect()

# def main():
#     """메인 함수"""
#     import argparse
    
#     parser = argparse.ArgumentParser(description='뉴스 크롤링 스케줄러')
#     parser.add_argument('--interval', type=int, default=1, 
#                        help='크롤링 간격 (시간, 기본값: 1)')
#     parser.add_argument('--once', action='store_true',
#                        help='한 번만 실행')
    
#     args = parser.parse_args()
    
#     scheduler = NewsScheduler()
    
#     try:
#         if args.once:
#             scheduler.run_once()
#         else:
#             scheduler.start_scheduler(args.interval)
#     except KeyboardInterrupt:
#         logger.info("프로그램 종료")
#     except Exception as e:
#         logger.error(f"프로그램 실행 중 오류: {e}")

# if __name__ == "__main__":
#     main() 
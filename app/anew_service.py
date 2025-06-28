import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from summary.services import NewsSummaryService
from summary.models import NewsSummaryRequest, NewsSummaryResponse, NewsSummaryItem
from database import mongodb

logger = logging.getLogger(__name__)

class AnewService:
    
    def __init__(self):
        self.news_summary_service = NewsSummaryService()
    
    def process_and_save_summary(self, 
                                news_list: List[Dict[str, Any]], 
                                max_length: Optional[int] = None):
        try:
            # 1. 뉴스 요약 요청 생성
            request = NewsSummaryRequest(
                news_list=news_list,
                max_length=max_length or 200
            )
            
            # 2. NewsSummaryService를 사용하여 요약 생성
            logger.info(f"뉴스 요약 시작: {len(news_list)}개 뉴스")
            summary_response = self.news_summary_service.summarize_news(request)
            
            # 3. NewsSummaryItem을 딕셔너리로 변환
            summary_items = []
            for item in summary_response.summary:
                summary_items.append({
                    "title": item.title,
                    "first_perspective": item.first_perspective,
                    "second_perspective": item.second_perspective,
                    "reference_url": item.reference_url
                })
            
            # 4. MongoDB에 저장
            logger.info(f"MongoDB에 요약 데이터 저장 시작: {len(summary_items)}개 요약")
            inserted_id = mongodb.insert_summary_items(summary_items)

            logger.info(f"요약 및 저장 완료: ID={inserted_id}")
        except Exception as e:
            logger.error(f"요약 및 저장 처리 중 오류 발생: {e}")
            raise Exception(f"요약 및 저장 처리 실패: {str(e)}")
    
    def get_recent_summary_item(self) -> Optional[Dict[str, Any]]:
        try:
            result = mongodb.get_recent_summary_item()
            if result:
                logger.info("최근 요약 데이터 조회 성공")
            else:
                logger.warning("저장된 요약 데이터가 없습니다")
            return result
        except Exception as e:
            logger.error(f"최근 요약 데이터 조회 실패: {e}")
            raise Exception(f"최근 요약 데이터 조회 실패: {str(e)}")
    
    def delete_summary_by_id(self, summary_id: str) -> bool:
        try:
            if mongodb.collection is None:
                raise Exception("MongoDB가 연결되지 않았습니다.")
            
            from bson import ObjectId
            result = mongodb.collection.delete_one({"_id": ObjectId(summary_id)})
            
            if result.deleted_count > 0:
                logger.info(f"요약 데이터 삭제 성공: ID={summary_id}")
                return True
            else:
                logger.warning(f"삭제할 요약 데이터를 찾을 수 없음: ID={summary_id}")
                return False
                
        except Exception as e:
            logger.error(f"요약 데이터 삭제 실패: ID={summary_id}, 오류={e}")
            raise Exception(f"요약 데이터 삭제 실패: {str(e)}")

anew_service = AnewService() 
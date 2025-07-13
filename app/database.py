from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from config import settings
from logger import get_logger
from typing import Optional, Dict, List, Any
from bson import ObjectId
from datetime import datetime

logger = get_logger()

def convert_objectid_to_str(data: Any) -> Any:
    """MongoDB 결과에서 ObjectId를 문자열로 변환하는 유틸리티 함수"""
    if isinstance(data, dict):
        return {key: convert_objectid_to_str(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

class MongoDB:
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self.collection: Optional[Collection] = None
        
    def connect(self):
        try:
            self.client = MongoClient(settings.mongodb_uri)
            # 연결 테스트
            self.client.admin.command('ping')
            logger.info("MongoDB 연결 성공")
            
            self.database = self.client[settings.mongodb_database]
            self.collection = self.database[settings.mongodb_collection]
            
        except Exception as e:
            logger.error(f"MongoDB 연결 실패: {e}")
            raise Exception(f"MongoDB 연결에 실패했습니다: {str(e)}")
    
    def disconnect(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB 연결 해제")
    
    def get_collection(self) -> Collection:
        if self.collection is None:
            raise Exception("MongoDB가 연결되지 않았습니다. connect() 메서드를 먼저 호출하세요.")
        return self.collection
    
    
    def insert_summary_items(self, summary_items: list):
        """NewsSummaryItem 목록을 MongoDB에 저장"""
        try:
            if self.collection is None:
                raise Exception("MongoDB가 연결되지 않았습니다. connect() 메서드를 먼저 호출하세요.")
            
            # 저장할 데이터 구성
            data_to_insert = {
                "summary_items": summary_items,
                "created_at": datetime.now().isoformat(),
                "item_count": len(summary_items)
            }
            
            result = self.collection.insert_one(data_to_insert)
            logger.info(f"NewsSummaryItem 목록 저장 완료: {result}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"NewsSummaryItem 목록 저장 실패: {e}")
            raise Exception(f"데이터 저장에 실패했습니다: {str(e)}")
    
    def get_summary_items_by_id(self, summary_id: str) -> Optional[Dict[str, Any]]:
        """ID로 NewsSummaryItem 목록 조회"""
        try:
            if self.collection is None:
                raise Exception("MongoDB가 연결되지 않았습니다. connect() 메서드를 먼저 호출하세요.")
            result = self.collection.find_one({"_id": ObjectId(summary_id)})
            if result:
                return convert_objectid_to_str(result)
            return result
        except Exception as e:
            logger.error(f"NewsSummaryItem 목록 조회 실패: {e}")
            raise Exception(f"데이터 조회에 실패했습니다: {str(e)}")
    
    def get_all_summary_items(self, limit: int = 10) -> List[Dict[str, Any]]:
        """모든 NewsSummaryItem 목록 조회 (최신순)"""
        try:
            if self.collection is None:
                raise Exception("MongoDB가 연결되지 않았습니다. connect() 메서드를 먼저 호출하세요.")
            results = list(self.collection.find().sort("_id", -1).limit(limit))
            return convert_objectid_to_str(results)
        except Exception as e:
            logger.error(f"NewsSummaryItem 목록 조회 실패: {e}")
            raise Exception(f"데이터 목록 조회에 실패했습니다: {str(e)}")
    
    def get_recent_summary_item(self) -> Optional[Dict[str, Any]]:
        """가장 최근 NewsSummaryItem 조회"""
        try:
            if self.collection is None:
                raise Exception("MongoDB가 연결되지 않았습니다. connect() 메서드를 먼저 호출하세요.")
            result = self.collection.find_one(sort=[("_id", -1)])
            if result:
                return convert_objectid_to_str(result)
            return None
        except Exception as e:
            logger.error(f"NewsSummaryItem 조회 실패: {e}")
            raise Exception(f"데이터 조회에 실패했습니다: {str(e)}")

mongodb = MongoDB() 
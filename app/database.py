from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    def __init__(self):
        self.client: MongoClient = None
        self.database: Database = None
        self.collection: Collection = None
        
    def connect(self):
        """MongoDB에 연결"""
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
        """MongoDB 연결 해제"""
        if self.client:
            self.client.close()
            logger.info("MongoDB 연결 해제")
    
    def get_collection(self) -> Collection:
        """컬렉션 반환"""
        if not self.collection:
            raise Exception("MongoDB가 연결되지 않았습니다. connect() 메서드를 먼저 호출하세요.")
        return self.collection
    
    def insert_summary(self, summary_data: dict) -> str:
        """요약 데이터를 MongoDB에 저장"""
        try:
            result = self.collection.insert_one(summary_data)
            logger.info(f"요약 데이터 저장 완료: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"요약 데이터 저장 실패: {e}")
            raise Exception(f"데이터 저장에 실패했습니다: {str(e)}")
    
    def get_summary_by_id(self, summary_id: str) -> dict:
        """ID로 요약 데이터 조회"""
        try:
            from bson import ObjectId
            result = self.collection.find_one({"_id": ObjectId(summary_id)})
            if result:
                result["_id"] = str(result["_id"])  # ObjectId를 문자열로 변환
            return result
        except Exception as e:
            logger.error(f"요약 데이터 조회 실패: {e}")
            raise Exception(f"데이터 조회에 실패했습니다: {str(e)}")
    
    def get_all_summaries(self, limit: int = 10) -> list:
        """모든 요약 데이터 조회 (최신순)"""
        try:
            results = list(self.collection.find().sort("_id", -1).limit(limit))
            # ObjectId를 문자열로 변환
            for result in results:
                result["_id"] = str(result["_id"])
            return results
        except Exception as e:
            logger.error(f"요약 데이터 목록 조회 실패: {e}")
            raise Exception(f"데이터 목록 조회에 실패했습니다: {str(e)}")

# 전역 MongoDB 인스턴스
mongodb = MongoDB() 
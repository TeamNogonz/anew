from pydantic import BaseModel, Field
from typing import Optional

class NewsSummaryRequest(BaseModel):
    """뉴스 요약 요청 모델"""
    content: str = Field(..., description="요약할 뉴스 내용", min_length=10)
    max_length: Optional[int] = Field(default=200, description="요약 최대 길이", ge=50, le=1000)
    
class NewsSummaryResponse(BaseModel):
    """뉴스 요약 응답 모델"""
    original_length: int = Field(..., description="원본 텍스트 길이")
    summary: str = Field(..., description="요약된 내용")
    summary_length: int = Field(..., description="요약 텍스트 길이")
    compression_ratio: float = Field(..., description="압축 비율 (원본 대비 요약 길이)")
    
class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    error: str = Field(..., description="에러 메시지")
    detail: Optional[str] = Field(None, description="상세 에러 정보") 
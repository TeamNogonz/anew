from pydantic import BaseModel, Field
from typing import Optional, List

class NewsSummaryRequest(BaseModel):
    news_list: list[dict] = Field(..., description="뉴스 목록")
    max_length: Optional[int] = Field(default=200, description="요약 최대 길이", ge=50, le=1000)
    
class Perspective(BaseModel):
    title: str = Field(..., description="관점 이름")
    icon: str = Field(..., description="관점을 나타내는 이모지")
    perspectives: List[str] = Field(..., description="요약 문장들의 리스트")
    
class NewsSummaryItem(BaseModel):
    title: str = Field(..., description="주제 제목")
    first_perspective: Perspective = Field(..., description="첫 번째 관점")
    second_perspective: Perspective = Field(..., description="두 번째 관점")
    reference_url: List[str] = Field(..., description="참조 URL 목록")
    
class NewsSummaryResponse(BaseModel):
    summary: List[NewsSummaryItem] = Field(..., description="요약된 뉴스 목록")
    
class ErrorResponse(BaseModel):
    error: str = Field(..., description="에러 메시지")
    detail: Optional[str] = Field(None, description="상세 에러 정보") 
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from summary.services import NewsSummaryService
from database import mongodb
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

build_dir = os.path.join(os.path.dirname(__file__), "static")
static_assets_dir = os.path.join(build_dir, "static")

app.mount("/static", StaticFiles(directory=static_assets_dir), name="static")

news_service = None

def get_news_service() -> NewsSummaryService:
    global news_service
    if news_service is None:
        try:
            news_service = NewsSummaryService()
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))
    return news_service

# @app.on_event("startup")
# async def startup_event():
#     try:
#         mongodb/.connect()
        
#         # 뉴스 서비스 초기화
#         service = get_news_service()
#         if not service.validate_api_key():
#             logger.warning("Google API 키가 유효하지 않습니다. .env 파일을 확인해주세요.")
#         logger.info("server started..")
#     except Exception as e:
#         logger.error(f"서비스 초기화 중 오류: {e}")

# @app.on_event("shutdown")
# async def shutdown_event():
#     mongodb.disconnect()
#     logger.info("server shutdown..")

@app.get("/api/ping")
def ping():
    return {"message": "pong"}

summary = [
    {
        "title": "오징어 게임 시즌3 평가: 긍정적 vs 부정적",
        "first_perspective": {
            "title": "긍정적 관점",
            "icon": "👍",
            "perspectives": [
                "일부 외신은 시즌3이 전작의 잔혹함과 풍자를 계승하여 강렬한 마무리를 선사했다고 평가하며, 특히 마지막 에피소드의 반전과 연출을 높이 평가했다.",
                "돈이 인간성을 지배하는 세상을 비판하는 메시지도 여전히 유효하다고 보았다."
            ],
        },
        "second_perspective": {
            "title": "부정적 관점",
            "icon": "👎",
            "perspectives": [
                "많은 외신들은 시즌3이 전작들의 성공을 재현하지 못했다고 비판했다.",
                "반복적인 게임 구조와 평면적인 캐릭터, 부족한 상상력, 풍자의 감소 등을 지적하며 시즌1의 날카로운 메시지와 긴장감이 부족하다고 평가했다.",
                "시즌2의 실망스러운 평가를 극복하지 못했다는 의견도 다수였다."
            ],
        },
        "reference_url": [
            "https://n.news.naver.com/mnews/article/009/0005516242",
            "https://n.news.naver.com/mnews/article/009/0005516240"
        ]
    },
    {
        "title": "윤석열 전 대통령 내란 특검 조사: 정부 vs 야당 관점",
        "first_perspective": {
            "title": "정부 관점(특검 측)",
            "icon": "🏛️",
            "perspectives": [
                "윤석열 전 대통령의 공개 소환은 국민의 알 권리 충족과 수사의 투명성 확보 차원에서 필요한 조치였다.",
                "법적 절차에 따라 진행되었으며, 윤 전 대통령 측의 주장은 수사 방해 시도로 볼 수 있다."
            ],
        },
        "second_perspective": {
            "title": "야당 관점(윤 전 대통령 측)",
            "icon": "🗳️",
            "perspectives": [
                "특검의 공개 소환은 윤 전 대통령의 인권과 방어권을 심각하게 침해하는 행위이며, 변호인과의 사전 협의 없이 일방적으로 진행된 것은 법적 의무 위반이다.",
                "국민의 알 권리보다 특정인을 망신주기 위한 의도가 있다고 주장한다."
            ],
        },
        "reference_url": [
            "https://n.news.naver.com/mnews/article/009/0005516252",
            "https://n.news.naver.com/mnews/article/009/0005516241"
        ]
    },
    {
        "title": "중국 AI 산업 현황: 긍정적 vs 부정적 전망",
        "first_perspective": {
            "title": "긍정적 관점",
            "icon": "🤖",
            "perspectives": [
                "중국은 정부의 지원으로 AI 분야에서 괄목할 만한 성장을 이루었고, 딥시크와 같은 경쟁력 있는 모델을 개발했다.",
                "향후 기술 발전과 시장 확대 가능성이 높다."
            ],
        },
        "second_perspective": {
            "title": "부정적 관점",
            "icon": "⚠️",
            "perspectives": [
                "미국의 수출 규제로 인해 핵심 부품 확보에 어려움을 겪고 있으며, 과도한 경쟁으로 인해 수익성이 낮은 '좀비 AI'가 양산되고 있다.",
                "전기차 시장과 유사한 과잉 경쟁으로 인한 위기 가능성도 제기된다."
            ],
        },
        "reference_url": [
            "https://n.news.naver.com/mnews/article/009/0005516251"
        ]
    }
]

@app.get("/data")
def test_data():
    return summary

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str, request: Request):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    index_path = os.path.join(build_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {"message": "React app not found. Please build and place in static directory."}
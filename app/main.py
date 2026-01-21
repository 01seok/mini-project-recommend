"""
X-Style Clothing Recommendation Service

X 알고리즘의 핵심 원리를 차용한 옷 추천 서비스
- Multi-Action Prediction
- Pipeline Architecture
- Weighted Scoring
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.routers import recommend, engagement

app = FastAPI(
    title="X-Style Clothing Recommendation API",
    description="Multi-Action Prediction 기반 옷 추천 서비스",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(recommend.router, prefix="/api", tags=["Recommendation"])
app.include_router(engagement.router, prefix="/api", tags=["Engagement"])

# Static 파일 서빙
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.get("/", include_in_schema=False)
async def root():
    """테스트 웹 UI 제공"""
    index_path = os.path.join(static_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "X-Style Recommendation API", "docs": "/docs"}


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy"}

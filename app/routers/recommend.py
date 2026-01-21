"""
추천 API 라우터
"""

from typing import List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.services.recommendation import recommendation_service
from app.models.item import ScoredItem, ActionScores
from app.data.sample_data import init_sample_data
from app.data.store import item_store

router = APIRouter()


class RecommendationResponse(BaseModel):
    """추천 응답"""
    status: str
    message: str
    user_id: str
    recommendations: List[dict]
    total: int


@router.on_event("startup")
async def startup_event():
    """서버 시작 시 샘플 데이터 로드"""
    if not item_store.get_all_items():
        init_sample_data()


@router.get("/recommend", response_model=RecommendationResponse)
async def get_recommendations(
    user_id: str = Query(..., description="사용자 ID"),
    count: int = Query(10, ge=1, le=50, description="추천 개수"),
    seen_items: Optional[str] = Query(None, description="이미 본 상품 ID (쉼표 구분)"),
):
    """
    X 스타일 추천 목록 조회
    
    Multi-Action Prediction + Weighted Scoring + Diversity
    """
    seen_list = seen_items.split(",") if seen_items else []
    
    recommendations = recommendation_service.get_recommendations(
        user_id=user_id,
        count=count,
        seen_items=seen_list,
    )
    
    # 응답 포맷팅
    result = []
    for scored_item in recommendations:
        item = scored_item.item
        scores = scored_item.action_scores
        
        result.append({
            "item": {
                "id": item.id,
                "name": item.name,
                "brand": item.brand,
                "category": item.category.value,
                "price": item.price,
                "image_url": item.image_url,
                "style_tags": item.style_tags,
            },
            "scores": {
                "like": round(scores.like, 3),
                "click": round(scores.click, 3),
                "add_to_cart": round(scores.add_to_cart, 3),
                "purchase": round(scores.purchase, 3),
                "share": round(scores.share, 3),
                "not_interested": round(scores.not_interested, 3),
                "hide": round(scores.hide, 3),
            },
            "final_score": round(scored_item.final_score, 3),
            "diversity_penalty": round(scored_item.diversity_penalty, 3),
            "source": scored_item.source,
        })
    
    return RecommendationResponse(
        status="success",
        message="X-style recommendations generated",
        user_id=user_id,
        recommendations=result,
        total=len(result),
    )


@router.get("/items")
async def get_all_items():
    """전체 상품 목록 조회"""
    items = item_store.get_all_items()
    return {
        "status": "success",
        "items": [
            {
                "id": item.id,
                "name": item.name,
                "brand": item.brand,
                "category": item.category.value,
                "price": item.price,
                "image_url": item.image_url,
                "style_tags": item.style_tags,
            }
            for item in items
        ],
        "total": len(items),
    }

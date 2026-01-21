"""
사용자 행동 기록 API 라우터
"""

from typing import List
from fastapi import APIRouter
from pydantic import BaseModel

from app.services.engagement import engagement_service
from app.models.engagement import EngagementRequest, ActionType

router = APIRouter()


class EngagementResponse(BaseModel):
    """행동 기록 응답"""
    status: str
    message: str
    user_id: str
    item_id: str
    action_type: str


class HistoryResponse(BaseModel):
    """히스토리 조회 응답"""
    status: str
    user_id: str
    history: List[dict]
    total: int


@router.post("/engagement", response_model=EngagementResponse)
async def record_engagement(request: EngagementRequest):
    """
    사용자 행동 기록
    
    지원 행동: like, click, add_to_cart, purchase, share, not_interested, hide
    """
    engagement = engagement_service.record_engagement(request)
    
    return EngagementResponse(
        status="success",
        message=f"Recorded {request.action_type.value} action",
        user_id=engagement.user_id,
        item_id=engagement.item_id,
        action_type=engagement.action_type.value,
    )


@router.get("/engagement/{user_id}/history", response_model=HistoryResponse)
async def get_user_history(user_id: str):
    """사용자 행동 히스토리 조회"""
    history = engagement_service.get_user_history(user_id)
    
    return HistoryResponse(
        status="success",
        user_id=user_id,
        history=[
            {
                "item_id": e.item_id,
                "action_type": e.action_type.value,
                "timestamp": e.timestamp.isoformat(),
            }
            for e in history
        ],
        total=len(history),
    )


@router.delete("/engagement/{user_id}/history")
async def clear_user_history(user_id: str):
    """사용자 행동 히스토리 초기화"""
    engagement_service.clear_user_history(user_id)
    
    return {
        "status": "success",
        "message": f"Cleared history for user {user_id}",
    }

"""
사용자 행동 기록 서비스

X 알고리즘의 User Action Sequence 관리
"""

from datetime import datetime
from app.models.engagement import Engagement, EngagementRequest, ActionType
from app.data.store import engagement_store


class EngagementService:
    """사용자 행동 기록 서비스"""
    
    def record_engagement(self, request: EngagementRequest) -> Engagement:
        """
        사용자 행동 기록
        
        Args:
            request: 행동 기록 요청
        
        Returns:
            생성된 Engagement 객체
        """
        engagement = Engagement(
            user_id=request.user_id,
            item_id=request.item_id,
            action_type=request.action_type,
            timestamp=datetime.now(),
        )
        
        engagement_store.add_engagement(engagement)
        
        return engagement
    
    def get_user_history(self, user_id: str) -> list[Engagement]:
        """사용자 히스토리 조회"""
        return engagement_store.get_user_history(user_id)
    
    def clear_user_history(self, user_id: str) -> None:
        """사용자 히스토리 초기화"""
        engagement_store.clear_user_history(user_id)


# 전역 서비스 인스턴스
engagement_service = EngagementService()

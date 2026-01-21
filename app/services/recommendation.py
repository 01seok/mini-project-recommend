"""
추천 서비스

X 알고리즘 스타일 파이프라인 실행
1. Query Hydration: 사용자 히스토리 조회
2. Candidate Sourcing: In-Network + Out-of-Network
3. Filtering: 중복/본 상품 제거
4. Scoring: Multi-Action + Weighted + Diversity
5. Selection: Top-K
"""

from typing import List, Optional
from app.models.item import Item, ScoredItem, ActionScores
from app.models.user import User
from app.pipeline.base import PipelineContext
from app.pipeline.sources import CombinedSource
from app.pipeline.filters import CompositeFilter, DuplicateFilter, SeenItemsFilter, EngagedItemsFilter
from app.pipeline.scorers import CompositeScorer, MultiActionScorer, WeightedScorer, DiversityScorer
from app.pipeline.selectors import TopKSelector
from app.data.store import user_store, engagement_store, item_store
from app.config import DEFAULT_RECOMMENDATION_COUNT


class RecommendationService:
    """
    X 알고리즘 스타일 추천 서비스
    
    파이프라인 단계:
    Request → Query Hydration → Candidate Sources → 
    Filtering → Scoring → Selection → Response
    """
    
    def __init__(self):
        # 파이프라인 컴포넌트 초기화
        self.source = CombinedSource()
        
        self.filter = CompositeFilter([
            DuplicateFilter(),
            SeenItemsFilter(),
            EngagedItemsFilter(),
        ])
        
        self.scorer = CompositeScorer([
            MultiActionScorer(),   # Multi-Action Prediction
            WeightedScorer(),      # Weighted Scoring
            DiversityScorer(),     # Author (Brand) Diversity
        ])
        
        self.selector = TopKSelector()
    
    def get_recommendations(
        self,
        user_id: str,
        count: int = DEFAULT_RECOMMENDATION_COUNT,
        seen_items: List[str] = None,
    ) -> List[ScoredItem]:
        """
        추천 목록 반환
        
        Args:
            user_id: 사용자 ID
            count: 추천 개수
            seen_items: 이미 본 상품 ID 목록
        
        Returns:
            점수화된 추천 상품 목록
        """
        
        # 1. Query Hydration: 사용자 정보 및 히스토리 조회
        user = user_store.get_user(user_id)
        if not user:
            # 새 사용자는 기본 설정으로 생성
            user = User(id=user_id, name=f"User {user_id}")
        
        engagement_history = engagement_store.get_user_history(user_id)
        
        context = PipelineContext(
            user=user,
            engagement_history=engagement_history,
            seen_items=seen_items or [],
        )
        
        # 2. Candidate Sourcing
        candidates = self.source.get_candidates(context)
        
        if not candidates:
            # 후보가 없으면 전체 상품에서 랜덤 추천
            candidates = item_store.get_all_items()
        
        # 3. Filtering
        filtered = self.filter.filter(candidates, context)
        
        # 4. Item → ScoredItem 변환
        scored_items = [
            ScoredItem(
                item=item,
                action_scores=ActionScores(),
                source="in_network" if item.brand in user.preferred_brands else "out_of_network"
            )
            for item in filtered
        ]
        
        # 5. Scoring (Multi-Action → Weighted → Diversity)
        scored = self.scorer.score(scored_items, context)
        
        # 6. Selection (Top-K)
        selected = self.selector.select(scored, count)
        
        return selected


# 전역 서비스 인스턴스
recommendation_service = RecommendationService()

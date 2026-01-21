"""
파이프라인 기본 추상 클래스

X 알고리즘의 Candidate Pipeline 구조를 Python으로 구현
https://github.com/xai-org/x-algorithm/tree/main/candidate-pipeline

파이프라인 단계:
1. Source: 후보 아이템 소싱
2. Hydrator: 메타데이터 보강
3. Filter: 부적합 후보 제거
4. Scorer: 점수 계산
5. Selector: Top-K 선택
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.models.item import Item, ScoredItem
from app.models.user import User
from app.models.engagement import Engagement


class PipelineContext:
    """
    파이프라인 실행 컨텍스트
    
    X 알고리즘의 Query Hydration 결과를 담는 객체
    """
    def __init__(
        self,
        user: User,
        engagement_history: List[Engagement],
        seen_items: List[str] = None,
    ):
        self.user = user
        self.engagement_history = engagement_history
        self.seen_items = seen_items or []
        self.metadata: Dict[str, Any] = {}


class Source(ABC):
    """
    후보 소싱 추상 클래스
    
    X 알고리즘:
    - Thunder (In-Network): 팔로우한 계정의 포스트
    - Phoenix Retrieval (Out-of-Network): 전체 코퍼스에서 검색
    """
    
    @abstractmethod
    def get_candidates(self, context: PipelineContext) -> List[Item]:
        """후보 아이템 반환"""
        pass


class Hydrator(ABC):
    """
    데이터 보강 추상 클래스
    
    X 알고리즘: Candidate Hydration
    - 상품 상세 정보
    - 브랜드 정보
    - 재고 상태 등
    """
    
    @abstractmethod
    def hydrate(self, items: List[Item], context: PipelineContext) -> List[Item]:
        """아이템에 추가 정보 보강"""
        pass


class Filter(ABC):
    """
    필터링 추상 클래스
    
    X 알고리즘 Pre-Scoring Filters:
    - DropDuplicatesFilter
    - AgeFilter
    - PreviouslySeenPostsFilter
    - MutedKeywordFilter 등
    """
    
    @abstractmethod
    def filter(self, items: List[Item], context: PipelineContext) -> List[Item]:
        """조건에 맞지 않는 아이템 제거"""
        pass


class Scorer(ABC):
    """
    점수 계산 추상 클래스
    
    X 알고리즘 Scoring:
    - Phoenix Scorer: ML 예측
    - Weighted Scorer: 가중 합산
    - Author Diversity Scorer: 다양성 조정
    """
    
    @abstractmethod
    def score(self, items: List[ScoredItem], context: PipelineContext) -> List[ScoredItem]:
        """아이템 점수 계산"""
        pass


class Selector(ABC):
    """
    선택 추상 클래스
    
    X 알고리즘: Selection
    - 점수 기준 정렬
    - Top-K 선택
    """
    
    @abstractmethod
    def select(self, items: List[ScoredItem], k: int) -> List[ScoredItem]:
        """상위 K개 아이템 선택"""
        pass

"""
필터링 (Pre-Scoring Filters)

X 알고리즘 Pre-Scoring Filters:
- DropDuplicatesFilter: 중복 제거
- AgeFilter: 오래된 상품 제거
- PreviouslySeenPostsFilter: 이미 본 상품 제거
"""

from typing import List, Set
from app.pipeline.base import Filter, PipelineContext
from app.models.item import Item


class DuplicateFilter(Filter):
    """
    중복 제거 필터
    
    X 알고리즘: DropDuplicatesFilter
    """
    
    def filter(self, items: List[Item], context: PipelineContext) -> List[Item]:
        seen_ids: Set[str] = set()
        unique_items = []
        
        for item in items:
            if item.id not in seen_ids:
                seen_ids.add(item.id)
                unique_items.append(item)
        
        return unique_items


class SeenItemsFilter(Filter):
    """
    이미 본 상품 제거 필터
    
    X 알고리즘: PreviouslySeenPostsFilter, PreviouslyServedPostsFilter
    """
    
    def filter(self, items: List[Item], context: PipelineContext) -> List[Item]:
        return [item for item in items if item.id not in context.seen_items]


class AgeFilter(Filter):
    """
    오래된 상품 제거 필터
    
    X 알고리즘: AgeFilter
    - 여기서는 별도 timestamp가 없으므로 패스스루
    """
    
    def filter(self, items: List[Item], context: PipelineContext) -> List[Item]:
        # 현재는 모든 상품 통과 (실제 구현 시 생성일 기준 필터링)
        return items


class EngagedItemsFilter(Filter):
    """
    이미 상호작용한 상품 필터
    
    사용자가 이미 like/purchase 등의 행동을 한 상품 제외
    """
    
    def filter(self, items: List[Item], context: PipelineContext) -> List[Item]:
        engaged_item_ids = {e.item_id for e in context.engagement_history}
        return [item for item in items if item.id not in engaged_item_ids]


class CompositeFilter(Filter):
    """
    여러 필터를 순차적으로 적용
    """
    
    def __init__(self, filters: List[Filter]):
        self.filters = filters
    
    def filter(self, items: List[Item], context: PipelineContext) -> List[Item]:
        result = items
        for f in self.filters:
            result = f.filter(result, context)
        return result

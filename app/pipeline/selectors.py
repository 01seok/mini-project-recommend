"""
선택 (Selection)

X 알고리즘: Selection
- 점수 기준 정렬
- Top-K 선택
"""

from typing import List
from app.pipeline.base import Selector
from app.models.item import ScoredItem


class TopKSelector(Selector):
    """
    Top-K 선택
    
    X 알고리즘: Sort by score, select top K candidates
    """
    
    def select(self, items: List[ScoredItem], k: int) -> List[ScoredItem]:
        # 최종 점수 기준 정렬
        sorted_items = sorted(items, key=lambda x: x.final_score, reverse=True)
        
        # 상위 K개 반환
        return sorted_items[:k]

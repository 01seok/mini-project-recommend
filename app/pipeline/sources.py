"""
후보 소싱 (Candidate Sources)

X 알고리즘:
- Thunder (In-Network): 팔로우한 계정의 포스트
- Phoenix Retrieval (Out-of-Network): ML 기반 전체 코퍼스 검색
"""

from typing import List
from app.pipeline.base import Source, PipelineContext
from app.models.item import Item
from app.data.store import item_store


class InNetworkSource(Source):
    """
    In-Network 소싱
    
    X 알고리즘의 Thunder에 해당
    - 사용자가 팔로우/선호하는 브랜드의 상품
    - 선호 스타일/카테고리 상품
    """
    
    def get_candidates(self, context: PipelineContext) -> List[Item]:
        candidates = []
        all_items = item_store.get_all_items()
        
        for item in all_items:
            # 선호 브랜드 매칭
            if item.brand in context.user.preferred_brands:
                candidates.append(item)
                continue
            
            # 선호 스타일 매칭
            if any(tag in context.user.preferred_styles for tag in item.style_tags):
                candidates.append(item)
                continue
            
            # 선호 카테고리 매칭
            if item.category.value in context.user.preferred_categories:
                candidates.append(item)
        
        return candidates


class OutOfNetworkSource(Source):
    """
    Out-of-Network 소싱
    
    X 알고리즘의 Phoenix Retrieval에 해당
    - 전체 상품 풀에서 검색
    - 사용자 히스토리 기반 유사도 검색 (간소화 버전)
    """
    
    def get_candidates(self, context: PipelineContext) -> List[Item]:
        all_items = item_store.get_all_items()
        
        # In-Network에서 가져온 것 제외 (별도 처리 필요 시)
        # 여기서는 전체 반환 (필터에서 중복 제거)
        return all_items


class CombinedSource(Source):
    """
    In-Network + Out-of-Network 결합 소싱
    
    X 알고리즘: 두 소스를 결합하여 후보 풀 구성
    """
    
    def __init__(self):
        self.in_network = InNetworkSource()
        self.out_of_network = OutOfNetworkSource()
    
    def get_candidates(self, context: PipelineContext) -> List[Item]:
        in_network_items = self.in_network.get_candidates(context)
        out_of_network_items = self.out_of_network.get_candidates(context)
        
        # 중복 제거하며 결합 (In-Network 우선)
        seen_ids = set()
        combined = []
        
        for item in in_network_items:
            if item.id not in seen_ids:
                seen_ids.add(item.id)
                combined.append(item)
        
        for item in out_of_network_items:
            if item.id not in seen_ids:
                seen_ids.add(item.id)
                combined.append(item)
        
        return combined

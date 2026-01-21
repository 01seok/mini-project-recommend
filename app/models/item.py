"""
상품 모델

X 알고리즘의 Candidate에 해당
"""

from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum


class Category(str, Enum):
    """상품 카테고리"""
    UPPER = "upper"      # 상의
    LOWER = "lower"      # 하의
    OUTER = "outer"      # 아우터
    SHOES = "shoes"      # 신발
    ACCESSORY = "accessory"  # 액세서리


class Item(BaseModel):
    """상품 정보"""
    id: str
    name: str
    brand: str
    category: Category
    price: int
    image_url: str
    style_tags: List[str] = []
    embedding: Optional[List[float]] = None  # 이미지/텍스트 임베딩


class ActionScores(BaseModel):
    """
    Multi-Action Prediction 결과
    
    X 알고리즘 핵심: 단일 점수가 아닌 여러 행동에 대한 확률 예측
    """
    like: float = 0.0           # P(좋아요)
    click: float = 0.0          # P(클릭)
    add_to_cart: float = 0.0    # P(장바구니)
    purchase: float = 0.0       # P(구매)
    share: float = 0.0          # P(공유)
    not_interested: float = 0.0  # P(관심없음)
    hide: float = 0.0           # P(숨김)


class ScoredItem(BaseModel):
    """
    점수화된 상품
    
    파이프라인 Scoring 단계 이후의 결과
    """
    item: Item
    action_scores: ActionScores
    final_score: float = 0.0
    diversity_penalty: float = 1.0  # 다양성 패널티 (1.0 = 패널티 없음)
    source: str = "unknown"  # in_network / out_of_network

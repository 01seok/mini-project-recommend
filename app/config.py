"""
설정 모듈
"""

from typing import Dict

# 행동별 가중치 (X 알고리즘의 Weighted Scoring 원리)
ACTION_WEIGHTS: Dict[str, float] = {
    "like": 1.0,           # 좋아요
    "click": 0.5,          # 클릭
    "add_to_cart": 1.5,    # 장바구니 추가
    "purchase": 3.0,       # 구매
    "share": 2.0,          # 공유
    "not_interested": -1.0,  # 관심없음 (negative)
    "hide": -2.0,          # 숨김 (negative)
}

# 다양성 설정
DIVERSITY_DECAY = 0.8  # 동일 브랜드 반복 시 점수 감쇠율

# 추천 설정
DEFAULT_RECOMMENDATION_COUNT = 20
MAX_CANDIDATES = 100

"""
점수 계산 (Scoring)

X 알고리즘 Scoring 핵심 원리:
1. Multi-Action Prediction: 여러 행동 확률 예측
2. Weighted Scoring: 가중 합산
3. Author Diversity: 다양성 조정
"""

from typing import List, Dict
from collections import defaultdict
import math

from app.pipeline.base import Scorer, PipelineContext
from app.models.item import Item, ScoredItem, ActionScores
from app.models.engagement import ActionType
from app.config import ACTION_WEIGHTS, DIVERSITY_DECAY


class MultiActionScorer(Scorer):
    """
    다중 행동 확률 예측 (Multi-Action Prediction)
    
    X 알고리즘 핵심: Phoenix Scorer
    - P(like), P(click), P(purchase) 등 여러 행동 확률 예측
    
    간소화 구현:
    - 사용자 히스토리 기반 확률 계산
    - 실제 X는 Grok 기반 Transformer 사용
    """
    
    def score(self, items: List[ScoredItem], context: PipelineContext) -> List[ScoredItem]:
        # 사용자 히스토리 분석
        brand_affinity = self._calculate_brand_affinity(context)
        style_affinity = self._calculate_style_affinity(context)
        category_affinity = self._calculate_category_affinity(context)
        
        for scored_item in items:
            item = scored_item.item
            
            # 각 행동별 확률 계산 (0.0 ~ 1.0)
            base_score = 0.1  # 기본 확률
            
            # 브랜드 친화도
            brand_boost = brand_affinity.get(item.brand, 0.0)
            
            # 스타일 친화도
            style_boost = max(
                (style_affinity.get(tag, 0.0) for tag in item.style_tags),
                default=0.0
            )
            
            # 카테고리 친화도
            category_boost = category_affinity.get(item.category.value, 0.0)
            
            # 종합 부스트
            total_boost = (brand_boost + style_boost + category_boost) / 3
            
            # Multi-Action Scores 계산
            scored_item.action_scores = ActionScores(
                like=min(1.0, base_score + total_boost * 0.8 + brand_boost * 0.2),
                click=min(1.0, base_score + total_boost * 0.6),
                add_to_cart=min(1.0, base_score * 0.5 + total_boost * 0.4),
                purchase=min(1.0, base_score * 0.3 + total_boost * 0.3),
                share=min(1.0, base_score * 0.2 + total_boost * 0.2),
                not_interested=max(0.0, 0.1 - total_boost * 0.3),
                hide=max(0.0, 0.05 - total_boost * 0.2),
            )
        
        return items
    
    def _calculate_brand_affinity(self, context: PipelineContext) -> Dict[str, float]:
        """브랜드 친화도 계산 (히스토리 기반)"""
        from app.data.store import item_store
        
        brand_counts: Dict[str, float] = defaultdict(float)
        
        for engagement in context.engagement_history:
            item = item_store.get_item(engagement.item_id)
            if item:
                weight = ACTION_WEIGHTS.get(engagement.action_type.value, 0.5)
                brand_counts[item.brand] += max(0, weight)
        
        # 정규화
        if brand_counts:
            max_count = max(brand_counts.values())
            if max_count > 0:
                return {k: v / max_count for k, v in brand_counts.items()}
        
        return brand_counts
    
    def _calculate_style_affinity(self, context: PipelineContext) -> Dict[str, float]:
        """스타일 친화도 계산"""
        from app.data.store import item_store
        
        style_counts: Dict[str, float] = defaultdict(float)
        
        for engagement in context.engagement_history:
            item = item_store.get_item(engagement.item_id)
            if item:
                weight = ACTION_WEIGHTS.get(engagement.action_type.value, 0.5)
                for tag in item.style_tags:
                    style_counts[tag] += max(0, weight)
        
        if style_counts:
            max_count = max(style_counts.values())
            if max_count > 0:
                return {k: v / max_count for k, v in style_counts.items()}
        
        return style_counts
    
    def _calculate_category_affinity(self, context: PipelineContext) -> Dict[str, float]:
        """카테고리 친화도 계산"""
        from app.data.store import item_store
        
        category_counts: Dict[str, float] = defaultdict(float)
        
        for engagement in context.engagement_history:
            item = item_store.get_item(engagement.item_id)
            if item:
                weight = ACTION_WEIGHTS.get(engagement.action_type.value, 0.5)
                category_counts[item.category.value] += max(0, weight)
        
        if category_counts:
            max_count = max(category_counts.values())
            if max_count > 0:
                return {k: v / max_count for k, v in category_counts.items()}
        
        return category_counts


class WeightedScorer(Scorer):
    """
    가중 점수 합산 (Weighted Scoring)
    
    X 알고리즘 핵심: Weighted Scorer
    Final Score = Σ (weight × P(action))
    
    - 긍정 행동 (like, purchase): 양의 가중치
    - 부정 행동 (not_interested, hide): 음의 가중치
    """
    
    def score(self, items: List[ScoredItem], context: PipelineContext) -> List[ScoredItem]:
        for scored_item in items:
            scores = scored_item.action_scores
            
            # 가중 합산 (X 알고리즘 핵심 공식)
            final_score = (
                ACTION_WEIGHTS["like"] * scores.like +
                ACTION_WEIGHTS["click"] * scores.click +
                ACTION_WEIGHTS["add_to_cart"] * scores.add_to_cart +
                ACTION_WEIGHTS["purchase"] * scores.purchase +
                ACTION_WEIGHTS["share"] * scores.share +
                ACTION_WEIGHTS["not_interested"] * scores.not_interested +
                ACTION_WEIGHTS["hide"] * scores.hide
            )
            
            scored_item.final_score = final_score
        
        return items


class DiversityScorer(Scorer):
    """
    다양성 점수 조정 (Author Diversity Scorer)
    
    X 알고리즘: Author Diversity Scorer
    - 동일 브랜드가 연속으로 나오면 점수 감쇠
    - 특정 브랜드 편중 방지
    """
    
    def score(self, items: List[ScoredItem], context: PipelineContext) -> List[ScoredItem]:
        # 먼저 점수순 정렬
        sorted_items = sorted(items, key=lambda x: x.final_score, reverse=True)
        
        # 브랜드별 등장 횟수 추적
        brand_counts: Dict[str, int] = defaultdict(int)
        
        for scored_item in sorted_items:
            brand = scored_item.item.brand
            count = brand_counts[brand]
            
            # 다양성 패널티 적용
            penalty = DIVERSITY_DECAY ** count
            scored_item.diversity_penalty = penalty
            scored_item.final_score *= penalty
            
            brand_counts[brand] += 1
        
        return sorted_items


class CompositeScorer(Scorer):
    """
    여러 Scorer를 순차적으로 적용
    
    X 알고리즘: Phoenix Scorer → Weighted Scorer → Author Diversity Scorer
    """
    
    def __init__(self, scorers: List[Scorer]):
        self.scorers = scorers
    
    def score(self, items: List[ScoredItem], context: PipelineContext) -> List[ScoredItem]:
        result = items
        for scorer in self.scorers:
            result = scorer.score(result, context)
        return result

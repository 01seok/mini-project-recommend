"""
추천 시스템 평가 모듈

NDCG (Normalized Discounted Cumulative Gain) 메트릭을 사용한 평가
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class EvaluationResult:
    """평가 결과"""
    ndcg_at_5: float
    ndcg_at_10: float
    ndcg_at_20: float
    precision_at_5: float
    precision_at_10: float
    recall_at_10: float
    mrr: float  # Mean Reciprocal Rank
    num_users: int
    
    def to_dict(self) -> Dict:
        return {
            'NDCG@5': round(self.ndcg_at_5, 4),
            'NDCG@10': round(self.ndcg_at_10, 4),
            'NDCG@20': round(self.ndcg_at_20, 4),
            'Precision@5': round(self.precision_at_5, 4),
            'Precision@10': round(self.precision_at_10, 4),
            'Recall@10': round(self.recall_at_10, 4),
            'MRR': round(self.mrr, 4),
            'num_users': self.num_users,
        }
    
    def __str__(self) -> str:
        return (
            f"📊 Evaluation Results (n={self.num_users} users)\n"
            f"├─ NDCG@5:       {self.ndcg_at_5:.4f}\n"
            f"├─ NDCG@10:      {self.ndcg_at_10:.4f}\n"
            f"├─ NDCG@20:      {self.ndcg_at_20:.4f}\n"
            f"├─ Precision@5:  {self.precision_at_5:.4f}\n"
            f"├─ Precision@10: {self.precision_at_10:.4f}\n"
            f"├─ Recall@10:    {self.recall_at_10:.4f}\n"
            f"└─ MRR:          {self.mrr:.4f}"
        )


def dcg_at_k(relevance_scores: List[float], k: int) -> float:
    """
    DCG@k (Discounted Cumulative Gain at k)
    
    DCG@k = Σ (2^rel_i - 1) / log2(i + 1)
    """
    relevance = np.asarray(relevance_scores)[:k]
    n = len(relevance)
    if n == 0:
        return 0.0
    
    # Position weights: 1/log2(i+2) for i in 0..n-1
    positions = np.arange(1, n + 1)
    discounts = np.log2(positions + 1)
    
    # Gain: 2^rel - 1
    gains = np.power(2, relevance) - 1
    
    return float(np.sum(gains / discounts))


def ndcg_at_k(relevance_scores: List[float], k: int) -> float:
    """
    NDCG@k (Normalized DCG at k)
    
    NDCG@k = DCG@k / IDCG@k
    
    IDCG@k는 완벽한 순서(내림차순)일 때의 DCG
    """
    dcg = dcg_at_k(relevance_scores, k)
    
    # IDCG: 이상적인 순서 (내림차순)
    ideal_order = sorted(relevance_scores, reverse=True)
    idcg = dcg_at_k(ideal_order, k)
    
    if idcg == 0:
        return 0.0
    
    return dcg / idcg


def precision_at_k(relevant_items: set, recommended_items: List[str], k: int) -> float:
    """
    Precision@k: 추천된 상위 k개 중 관련 있는 아이템의 비율
    """
    if k == 0:
        return 0.0
    
    top_k = recommended_items[:k]
    hits = sum(1 for item in top_k if item in relevant_items)
    return hits / k


def recall_at_k(relevant_items: set, recommended_items: List[str], k: int) -> float:
    """
    Recall@k: 전체 관련 아이템 중 상위 k개에 포함된 비율
    """
    if len(relevant_items) == 0:
        return 0.0
    
    top_k = recommended_items[:k]
    hits = sum(1 for item in top_k if item in relevant_items)
    return hits / len(relevant_items)


def mrr(relevant_items: set, recommended_items: List[str]) -> float:
    """
    MRR (Mean Reciprocal Rank): 첫 번째 관련 아이템의 순위의 역수
    """
    for i, item in enumerate(recommended_items):
        if item in relevant_items:
            return 1.0 / (i + 1)
    return 0.0


class RecommenderEvaluator:
    """추천 시스템 평가기"""
    
    def __init__(self, items: List[Dict]):
        """
        Args:
            items: 상품 목록 (id, price, brand, category 등 포함)
        """
        self.items = items
        self.item_map = {item['id']: item for item in items}
    
    def compute_relevance(
        self,
        item_id: str,
        user_prefs: Dict
    ) -> float:
        """
        사용자 선호도 기반 관련성 점수 계산
        
        점수 범위: 0 (무관) ~ 3 (완전 일치)
        
        user_prefs:
            - preferred_brands: List[str]
            - preferred_categories: List[str]
            - price_range: Tuple[int, int]
            - purchased_items: List[str]  (정답 데이터)
        """
        item = self.item_map.get(item_id)
        if not item:
            return 0.0
        
        # 이미 구매한 아이템은 최고 점수
        if item_id in user_prefs.get('purchased_items', []):
            return 3.0
        
        score = 0.0
        
        # 브랜드 매칭
        if item.get('brand') in user_prefs.get('preferred_brands', []):
            score += 1.0
        
        # 카테고리 매칭
        if item.get('category') in user_prefs.get('preferred_categories', []):
            score += 1.0
        
        # 가격대 매칭
        price_range = user_prefs.get('price_range', (0, float('inf')))
        price = item.get('price', 0)
        if price_range[0] <= price <= price_range[1]:
            score += 0.5
        
        return score
    
    def evaluate_recommendations(
        self,
        recommended_ids: List[str],
        user_prefs: Dict,
        k_values: List[int] = [5, 10, 20]
    ) -> Dict[str, float]:
        """
        단일 사용자에 대한 추천 결과 평가
        """
        # 관련성 점수 계산
        relevance_scores = [
            self.compute_relevance(item_id, user_prefs)
            for item_id in recommended_ids
        ]
        
        # 관련 아이템 집합 (점수 > 0)
        relevant_items = {
            item_id for item_id, score in zip(recommended_ids, relevance_scores)
            if score > 0
        }
        
        # 실제 구매 아이템도 포함
        ground_truth = set(user_prefs.get('purchased_items', []))
        relevant_items.update(ground_truth)
        
        results = {}
        
        for k in k_values:
            results[f'ndcg@{k}'] = ndcg_at_k(relevance_scores, k)
            results[f'precision@{k}'] = precision_at_k(relevant_items, recommended_ids, k)
            results[f'recall@{k}'] = recall_at_k(ground_truth, recommended_ids, k) if ground_truth else 0.0
        
        results['mrr'] = mrr(relevant_items, recommended_ids)
        
        return results
    
    def aggregate_results(self, all_results: List[Dict[str, float]]) -> EvaluationResult:
        """
        여러 사용자의 결과를 집계
        """
        if not all_results:
            return EvaluationResult(0, 0, 0, 0, 0, 0, 0, 0)
        
        # 평균 계산
        avg = lambda key: np.mean([r.get(key, 0) for r in all_results])
        
        return EvaluationResult(
            ndcg_at_5=float(avg('ndcg@5')),
            ndcg_at_10=float(avg('ndcg@10')),
            ndcg_at_20=float(avg('ndcg@20')),
            precision_at_5=float(avg('precision@5')),
            precision_at_10=float(avg('precision@10')),
            recall_at_10=float(avg('recall@10')),
            mrr=float(avg('mrr')),
            num_users=len(all_results)
        )

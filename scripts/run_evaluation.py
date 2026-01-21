#!/usr/bin/env python3
"""
추천 시스템 평가 스크립트

무신사 크롤링 데이터를 사용하여 NDCG 평가 수행
"""

import sys
import json
import random
import argparse
from pathlib import Path
from typing import List, Dict

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.evaluation import RecommenderEvaluator, EvaluationResult
from app.services.recommendation import RecommendationService
from app.data.store import item_store, user_store, engagement_store
from app.models.item import Item, Category
from app.models.user import User


def load_musinsa_products(filepath: str) -> List[Dict]:
    """크롤링된 무신사 상품 로드"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def convert_to_items(products: List[Dict]) -> List[Item]:
    """Dict를 Item 모델로 변환"""
    items = []
    category_map = {
        'upper': Category.UPPER,
        'lower': Category.LOWER,
        'outer': Category.OUTER,
        'shoes': Category.SHOES,
        'accessory': Category.ACCESSORY,
    }
    
    for p in products:
        try:
            cat = category_map.get(p.get('category', 'upper'), Category.UPPER)
            item = Item(
                id=str(p['id']),
                name=p.get('name', f"Product {p['id']}")[:100],
                brand=p.get('brand', 'Unknown')[:50],
                category=cat,
                price=int(p.get('price', 0)),
                image_url=p.get('image_url', ''),
                style_tags=p.get('style_tags', []),
            )
            items.append(item)
        except Exception as e:
            print(f"  Warning: Skipping product {p.get('id')}: {e}")
    
    return items


def generate_synthetic_users(
    items: List[Item],
    num_users: int = 100
) -> List[Dict]:
    """
    합성 테스트 사용자 생성
    
    각 사용자는:
    - 선호 브랜드 2-4개
    - 선호 카테고리 1-2개
    - 가격대 범위
    - 가상의 구매 이력
    """
    users = []
    
    # 브랜드와 카테고리 목록
    brands = list(set(item.brand for item in items))
    categories = list(Category)
    
    for i in range(num_users):
        # 선호 브랜드 선택
        num_pref_brands = random.randint(2, min(4, len(brands)))
        preferred_brands = random.sample(brands, num_pref_brands)
        
        # 선호 카테고리 선택
        num_pref_cats = random.randint(1, 2)
        preferred_categories = [c.value for c in random.sample(categories, num_pref_cats)]
        
        # 가격대 설정
        price_min = random.choice([0, 20000, 50000, 100000])
        price_max = price_min + random.choice([50000, 100000, 200000, 500000])
        
        # 구매 이력 생성 (선호도에 맞는 아이템에서 샘플링)
        matching_items = [
            item for item in items
            if (item.brand in preferred_brands or item.category.value in preferred_categories)
            and price_min <= item.price <= price_max
        ]
        
        num_purchases = random.randint(3, min(10, len(matching_items)))
        if matching_items:
            purchased_items = [item.id for item in random.sample(matching_items, min(num_purchases, len(matching_items)))]
        else:
            purchased_items = []
        
        users.append({
            'user_id': f'eval_user_{i:03d}',
            'preferred_brands': preferred_brands,
            'preferred_categories': preferred_categories,
            'price_range': (price_min, price_max),
            'purchased_items': purchased_items,
        })
    
    return users


def run_evaluation(
    products_path: str,
    num_users: int = 100,
    top_k: int = 20
) -> EvaluationResult:
    """평가 실행"""
    
    print("🔄 Loading products...")
    products = load_musinsa_products(products_path)
    print(f"   Loaded {len(products)} products")
    
    print("\n🔄 Converting to Item models...")
    items = convert_to_items(products)
    print(f"   Converted {len(items)} items")
    
    print(f"\n🔄 Generating {num_users} synthetic users...")
    users = generate_synthetic_users(items, num_users)
    
    print("\n🔄 Setting up recommendation service...")
    # 전역 item_store에 아이템 로드
    item_store.clear()
    for item in items:
        item_store.add_item(item)
    
    # 평가자 설정
    evaluator = RecommenderEvaluator([p for p in products])
    
    # 추천 서비스 설정
    rec_service = RecommendationService()
    
    print(f"\n🚀 Running evaluation (top_k={top_k})...")
    all_results = []
    
    for i, user_prefs in enumerate(users):
        if (i + 1) % 20 == 0:
            print(f"   Progress: {i + 1}/{num_users}")
        
        # 사용자 생성
        user_obj = User(
            id=user_prefs['user_id'],
            name=f"Test User {i}",
            preferred_brands=user_prefs['preferred_brands'],
            preferred_categories=user_prefs['preferred_categories'],
        )
        user_store.add_user(user_obj)
        
        # 추천 수행
        try:
            recommendations = rec_service.get_recommendations(user_obj.id, count=top_k)
            recommended_ids = [rec.item.id for rec in recommendations]
            
            # 평가
            result = evaluator.evaluate_recommendations(
                recommended_ids,
                user_prefs,
                k_values=[5, 10, 20]
            )
            all_results.append(result)
        except Exception as e:
            print(f"   Warning: Error for user {user_prefs['user_id']}: {e}")
    
    # 결과 집계
    final_result = evaluator.aggregate_results(all_results)
    
    print("\n" + "=" * 50)
    print(final_result)
    print("=" * 50)
    
    return final_result


def main():
    parser = argparse.ArgumentParser(description='추천 시스템 평가')
    parser.add_argument(
        '--products',
        type=str,
        default='app/data/musinsa_products.json',
        help='크롤링된 상품 JSON 파일 경로'
    )
    parser.add_argument(
        '--users',
        type=int,
        default=100,
        help='테스트 사용자 수'
    )
    parser.add_argument(
        '--k',
        type=int,
        default=20,
        help='추천 아이템 수'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='랜덤 시드'
    )
    
    args = parser.parse_args()
    
    random.seed(args.seed)
    
    print("=" * 50)
    print("🎯 X-Style Recommendation System Evaluation")
    print("=" * 50)
    print(f"   Products: {args.products}")
    print(f"   Users: {args.users}")
    print(f"   Top-K: {args.k}")
    print(f"   Seed: {args.seed}")
    print()
    
    result = run_evaluation(args.products, args.users, args.k)
    
    # 결과 저장
    output_path = Path(__file__).parent / 'evaluation_results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result.to_dict(), f, indent=2)
    print(f"\n💾 Results saved to {output_path}")


if __name__ == '__main__':
    main()

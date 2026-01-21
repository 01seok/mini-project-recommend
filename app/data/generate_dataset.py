#!/usr/bin/env python3
"""
무신사 상품 데이터 생성기

실제 크롤링된 데이터를 기반으로 확장된 데이터셋 생성
"""

import json
import random
from pathlib import Path
from typing import List, Dict

# 실제 크롤링에서 추출한 브랜드 목록
REAL_BRANDS = [
    "퍼스텝", "메르시마리에", "신앤리", "엘리메노", "마리떼 프랑소와 저버",
    "커버낫", "디스이즈네버댓", "브라운브레스", "키르시", "널디",
    "스탠다드 플러스", "인사일런스", "맥케이트", "아더에러", "세터데이스",
    "페이탈리즘", "엠엘비", "예일", "앤더슨벨", "오버플로우",
    "무신사 스탠다드", "에잇세컨즈", "노이지클럽", "언더마이카", "니티드",
    "트래피스트", "스파오", "글로니", "마뗑킴", "인스턴트펑크",
    "비바스튜디오", "노스페이스", "파타고니아", "아이더", "디스커버리",
    "나이키", "아디다스", "뉴발란스", "컨버스", "반스",
    "라코스테", "타미힐피거", "폴로", "캘빈클라인", "리바이스"
]

# 유효한 실제 무신사 이미지 URL 풀
VALID_IMAGE_URLS = [
    "https://image.msscdn.net/thumbnails/images/goods_img/20240905/4412579/4412579_17255317387411_big.jpg?w=390",
    "https://image.msscdn.net/thumbnails/images/goods_img/20241213/4665941/4665941_17340749048855_big.jpg?w=390",
    "https://image.msscdn.net/thumbnails/images/goods_img/20240930/4474670/4474670_17276341073602_big.jpg?w=390",
    "https://image.msscdn.net/thumbnails/images/goods_img/20240904/4401734/4401734_17570606038936_big.jpg?w=390",
    "https://image.msscdn.net/thumbnails/images/goods_img/20250918/5486921/5486921_17592754933032_big.jpg?w=390",
    "https://image.msscdn.net/thumbnails/images/goods_img/20240305/3897421/3897421_17096427689507_big.jpg?w=390",
    "https://image.msscdn.net/thumbnails/images/goods_img/20240801/4298765/4298765_17193857392154_big.jpg?w=390",
    "https://image.msscdn.net/thumbnails/images/goods_img/20241015/4532198/4532198_17293547182937_big.jpg?w=390",
    "https://image.msscdn.net/thumbnails/images/goods_img/20241101/4587234/4587234_17304682719473_big.jpg?w=390",
    "https://image.msscdn.net/thumbnails/images/goods_img/20240612/4152873/4152873_17181023847612_big.jpg?w=390",
    "https://image.msscdn.net/thumbnails/images/goods_img/20240418/4068521/4068521_17154938271845_big.jpg?w=390",
    "https://image.msscdn.net/thumbnails/images/goods_img/20240521/4098765/4098765_17168923456712_big.jpg?w=390",
]

# 카테고리별 상품명 패턴
PRODUCT_PATTERNS = {
    "upper": [
        "{brand} 오버핏 반팔 티셔츠",
        "{brand} 헤비웨이트 후드 {color}",
        "{brand} 베이직 크루넥 맨투맨",
        "{brand} 스트라이프 긴팔 티",
        "{brand} 로고 자수 니트 {color}",
        "{brand} 캐시미어 블렌드 카디건",
        "{brand} 릴렉스드 핏 셔츠 {color}",
        "{brand} 하프집업 폴라 니트",
        "{brand} 빈티지 워싱 티셔츠",
        "{brand} 프린트 그래픽 후드티",
    ],
    "outer": [
        "{brand} 오버사이즈 블레이저 {color}",
        "{brand} 패딩 다운 자켓",
        "{brand} 플리스 집업 자켓",
        "{brand} 트렌치 코트 {color}",
        "{brand} 데님 트러커 자켓",
        "{brand} 봄버 자켓 {color}",
        "{brand} 윈드브레이커 재킷",
        "{brand} 울 싱글 코트",
        "{brand} 후드 패딩 베스트",
        "{brand} 레더 라이더 자켓",
    ],
    "lower": [
        "{brand} 와이드 핏 데님 팬츠",
        "{brand} 스트레이트 핏 치노 {color}",
        "{brand} 조거 팬츠 {color}",
        "{brand} 카고 팬츠 릴렉스드",
        "{brand} 슬랙스 {color}",
        "{brand} 숏 팬츠 {color}",
        "{brand} 트레이닝 팬츠",
        "{brand} 워크웨어 팬츠",
        "{brand} 플리츠 와이드 팬츠",
        "{brand} 코듀로이 팬츠 {color}",
    ],
    "shoes": [
        "{brand} 러닝화 {color}",
        "{brand} 캔버스 스니커즈",
        "{brand} 레더 로퍼",
        "{brand} 하이탑 스니커즈 {color}",
        "{brand} 청키 스니커즈",
        "{brand} 슬립온 스니커즈",
        "{brand} 첼시 부츠",
        "{brand} 워커 부츠 {color}",
        "{brand} 레트로 러닝화",
        "{brand} 샌들 슬리퍼",
    ],
    "accessory": [
        "{brand} 크로스백 {color}",
        "{brand} 백팩 라지",
        "{brand} 토트백 {color}",
        "{brand} 볼캡 {color}",
        "{brand} 비니 {color}",
        "{brand} 버킷햇",
        "{brand} 벨트 {color}",
        "{brand} 지갑 레더",
        "{brand} 에코백 {color}",
        "{brand} 스카프 울",
    ],
}

COLORS = ["블랙", "화이트", "네이비", "그레이", "베이지", "브라운", "카키", "버건디", "크림", "차콜"]

# 가격 범위 (카테고리별)
PRICE_RANGES = {
    "upper": (19900, 159000),
    "outer": (49000, 399000),
    "lower": (29000, 189000),
    "shoes": (39000, 259000),
    "accessory": (15000, 129000),
}


def generate_product(product_id: int, category: str) -> Dict:
    """단일 상품 생성"""
    brand = random.choice(REAL_BRANDS)
    pattern = random.choice(PRODUCT_PATTERNS[category])
    color = random.choice(COLORS)
    
    name = pattern.format(brand=brand, color=color)
    
    price_min, price_max = PRICE_RANGES[category]
    # 가격은 100원 단위로 반올림
    price = round(random.randint(price_min, price_max) / 100) * 100
    
    # 🌟 실제 이미지 URL 랜덤 할당
    image_url = random.choice(VALID_IMAGE_URLS)
    
    return {
        "id": str(product_id),
        "name": name,
        "brand": brand,
        "category": category,
        "price": price,
        "image_url": image_url,
        "style_tags": [],
    }


def add_real_crawled_products() -> List[Dict]:
    """실제 크롤링된 상품 추가"""
    # 실제 URL 맵핑 (우선순위 높음)
    return [
        {
            "id": "4412579",
            "brand": "퍼스텝",
            "name": "더 하이어 헤비웨이트 후드 네이비 JUHD4665",
            "price": 41570,
            "category": "upper",
            "image_url": "https://image.msscdn.net/thumbnails/images/goods_img/20240905/4412579/4412579_17255317387411_big.jpg?w=390"
        },
        {
            "id": "5425638",
            "brand": "메르시마리에",
            "name": "루즈핏 박시 목폴라 롱 니트 111834",
            "price": 31900,
            "category": "upper",
            "image_url": "https://image.msscdn.net/thumbnails/images/goods_img/20241213/4665941/4665941_17340749048855_big.jpg?w=390"
        },
        {
            "id": "4474670",
            "brand": "신앤리",
            "name": "(W) 테일러 코튼 스웻 후드 티셔츠 네이비",
            "price": 103200,
            "category": "upper",
            "image_url": "https://image.msscdn.net/thumbnails/images/goods_img/20240930/4474670/4474670_17276341073602_big.jpg?w=390"
        },
        {
            "id": "4401734",
            "brand": "엘리메노",
            "name": "EL 플랫 후드티셔츠 5Color",
            "price": 31410,
            "category": "upper",
            "image_url": "https://image.msscdn.net/thumbnails/images/goods_img/20240904/4401734/4401734_17570606038936_big.jpg?w=390"
        },
        {
            "id": "5486921",
            "brand": "마리떼 프랑소와 저버",
            "name": "CLASSIC LOGO EMBROIDERY HOODIE (BRUSHED) heather gray",
            "price": 83300,
            "category": "upper",
            "image_url": "https://image.msscdn.net/thumbnails/images/goods_img/20250918/5486921/5486921_17592754933032_big.jpg?w=390"
        },
    ]


def generate_dataset(total: int = 1000) -> List[Dict]:
    """전체 데이터셋 생성"""
    products = []
    
    # 실제 크롤링 데이터 추가
    products.extend(add_real_crawled_products())
    seen_ids = {p["id"] for p in products}
    
    categories = list(PRODUCT_PATTERNS.keys())
    per_category = (total - len(products)) // len(categories)
    
    product_id = 1000000  # 시작 ID
    
    for category in categories:
        for _ in range(per_category):
            while str(product_id) in seen_ids:
                product_id += 1
            
            product = generate_product(product_id, category)
            products.append(product)
            seen_ids.add(str(product_id))
            product_id += random.randint(1, 10)
    
    # 부족분 채우기
    while len(products) < total:
        category = random.choice(categories)
        while str(product_id) in seen_ids:
            product_id += 1
        
        product = generate_product(product_id, category)
        products.append(product)
        seen_ids.add(str(product_id))
        product_id += random.randint(1, 10)
    
    random.shuffle(products)
    return products[:total]


def main():
    """데이터 생성 및 저장"""
    random.seed(42)
    
    print("🏭 Generating Musinsa-style product dataset...")
    products = generate_dataset(1000)
    
    output_path = Path(__file__).parent / "musinsa_products.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Generated {len(products)} products")
    print(f"💾 Saved to {output_path}")
    
    # 통계
    categories = {}
    brands = {}
    for p in products:
        cat = p.get("category", "unknown")
        brand = p.get("brand", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
        brands[brand] = brands.get(brand, 0) + 1
    
    print(f"\n📊 Statistics:")
    print(f"   Categories: {categories}")
    print(f"   Unique brands: {len(brands)}")
    
    avg_price = sum(p["price"] for p in products) / len(products)
    print(f"   Average price: ₩{avg_price:,.0f}")


if __name__ == "__main__":
    main()

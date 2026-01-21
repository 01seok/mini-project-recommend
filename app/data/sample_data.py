"""
샘플 데이터 초기화

테스트를 위한 샘플 상품 및 사용자 데이터
실제 무신사 상품 이미지 URL 포함
"""

import json
from pathlib import Path
from app.models.item import Item, Category
from app.models.user import User
from app.data.store import item_store, user_store


def load_musinsa_products():
    """무신사 상품 JSON 로드"""
    json_path = Path(__file__).parent / "musinsa_products.json"
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def init_sample_data():
    """샘플 데이터 초기화 - 무신사 상품 사용"""
    
    # 무신사 상품 로드
    musinsa_products = load_musinsa_products()
    
    if musinsa_products:
        # JSON에서 로드
        category_map = {
            'upper': Category.UPPER,
            'lower': Category.LOWER,
            'outer': Category.OUTER,
            'shoes': Category.SHOES,
            'accessory': Category.ACCESSORY,
        }
        
        loaded_count = 0
        for p in musinsa_products[:100]:  # 샘플로 100개만 로드
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
                item_store.add_item(item)
                loaded_count += 1
            except Exception as e:
                print(f"  Warning: Skipping product {p.get('id')}: {e}")
        
        print(f"✅ Loaded {loaded_count} items from musinsa_products.json")
    else:
        # 폴백: 실제 무신사 이미지가 포함된 샘플 데이터
        sample_items = [
            Item(
                id="4412579",
                name="더 하이어 헤비웨이트 후드 네이비",
                brand="퍼스텝",
                category=Category.UPPER,
                price=41570,
                image_url="https://image.msscdn.net/thumbnails/images/goods_img/20240905/4412579/4412579_17255317387411_big.jpg?w=390",
                style_tags=["스트릿", "캐주얼", "후드"],
            ),
            Item(
                id="5425638",
                name="루즈핏 박시 목폴라 롱 니트",
                brand="메르시마리에",
                category=Category.UPPER,
                price=31900,
                image_url="https://image.msscdn.net/thumbnails/images/goods_img/20241213/4665941/4665941_17340749048855_big.jpg?w=390",
                style_tags=["캐주얼", "니트", "루즈핏"],
            ),
            Item(
                id="4474670",
                name="테일러 코튼 스웻 후드 티셔츠",
                brand="신앤리",
                category=Category.UPPER,
                price=103200,
                image_url="https://image.msscdn.net/thumbnails/images/goods_img/20240930/4474670/4474670_17276341073602_big.jpg?w=390",
                style_tags=["캐주얼", "베이직", "후드"],
            ),
            Item(
                id="4401734",
                name="EL 플랫 후드티셔츠",
                brand="엘리메노",
                category=Category.UPPER,
                price=31410,
                image_url="https://image.msscdn.net/thumbnails/images/goods_img/20240904/4401734/4401734_17570606038936_big.jpg?w=390",
                style_tags=["캐주얼", "베이직"],
            ),
            Item(
                id="5486921",
                name="CLASSIC LOGO EMBROIDERY HOODIE",
                brand="마리떼 프랑소와 저버",
                category=Category.UPPER,
                price=83300,
                image_url="https://image.msscdn.net/thumbnails/images/goods_img/20250918/5486921/5486921_17592754933032_big.jpg?w=390",
                style_tags=["스트릿", "로고", "후드"],
            ),
            # 하의
            Item(
                id="sample_101",
                name="와이드 데님 팬츠 블루",
                brand="무신사 스탠다드",
                category=Category.LOWER,
                price=59000,
                image_url="https://image.msscdn.net/thumbnails/images/goods_img/20240305/3897421/3897421_17096427689507_big.jpg?w=390",
                style_tags=["캐주얼", "와이드", "데님"],
            ),
            Item(
                id="sample_102",
                name="스트레이트 치노 팬츠",
                brand="커버낫",
                category=Category.LOWER,
                price=69000,
                image_url="https://image.msscdn.net/thumbnails/images/goods_img/20240801/4298765/4298765_17193857392154_big.jpg?w=390",
                style_tags=["캐주얼", "스트레이트"],
            ),
            # 아우터
            Item(
                id="sample_201",
                name="오버사이즈 블레이저",
                brand="디스이즈네버댓",
                category=Category.OUTER,
                price=189000,
                image_url="https://image.msscdn.net/thumbnails/images/goods_img/20241015/4532198/4532198_17293547182937_big.jpg?w=390",
                style_tags=["클래식", "오버핏", "블레이저"],
            ),
            Item(
                id="sample_202",
                name="플리스 집업 자켓",
                brand="파타고니아",
                category=Category.OUTER,
                price=219000,
                image_url="https://image.msscdn.net/thumbnails/images/goods_img/20241101/4587234/4587234_17304682719473_big.jpg?w=390",
                style_tags=["아웃도어", "플리스"],
            ),
            # 신발
            Item(
                id="sample_301",
                name="뉴발란스 993",
                brand="뉴발란스",
                category=Category.SHOES,
                price=259000,
                image_url="https://image.msscdn.net/thumbnails/images/goods_img/20240612/4152873/4152873_17181023847612_big.jpg?w=390",
                style_tags=["스포티", "러닝", "클래식"],
            ),
            Item(
                id="sample_302",
                name="척 70 하이탑",
                brand="컨버스",
                category=Category.SHOES,
                price=95000,
                image_url="https://image.msscdn.net/thumbnails/images/goods_img/20240418/4068521/4068521_17154938271845_big.jpg?w=390",
                style_tags=["캐주얼", "클래식", "캔버스"],
            ),
            Item(
                id="sample_303",
                name="에어포스 1 화이트",
                brand="나이키",
                category=Category.SHOES,
                price=139000,
                image_url="https://image.msscdn.net/thumbnails/images/goods_img/20240521/4098765/4098765_17168923456712_big.jpg?w=390",
                style_tags=["스트릿", "클래식", "화이트"],
            ),
        ]
        
        for item in sample_items:
            item_store.add_item(item)
        
        print(f"✅ Loaded {len(sample_items)} items with real Musinsa images")
    
    # 샘플 사용자 데이터
    sample_users = [
        User(
            id="user_001",
            name="캐주얼 러버",
            preferred_brands=["무신사 스탠다드", "커버낫", "퍼스텝"],
            preferred_styles=["캐주얼", "스트릿"],
            preferred_categories=["upper", "lower"],
        ),
        User(
            id="user_002",
            name="클래식 맨",
            preferred_brands=["무신사 스탠다드", "디스이즈네버댓", "마리떼 프랑소와 저버"],
            preferred_styles=["클래식", "포멀"],
            preferred_categories=["outer", "shoes"],
        ),
        User(
            id="user_003",
            name="스트릿 보이",
            preferred_brands=["퍼스텝", "커버낫", "나이키"],
            preferred_styles=["스트릿", "스포티"],
            preferred_categories=["upper", "shoes"],
        ),
        User(
            id="user_004",
            name="새로운 유저",
            preferred_brands=[],
            preferred_styles=[],
            preferred_categories=[],
        ),
    ]
    
    for user in sample_users:
        user_store.add_user(user)
    
    print(f"✅ Loaded {len(sample_users)} users")

"""
샘플 데이터 초기화

테스트를 위한 샘플 상품 및 사용자 데이터
"""

from app.models.item import Item, Category
from app.models.user import User
from app.data.store import item_store, user_store


def init_sample_data():
    """샘플 데이터 초기화"""
    
    # 샘플 상품 데이터
    sample_items = [
        # 상의 (UPPER)
        Item(
            id="item_001",
            name="오버핏 코튼 티셔츠",
            brand="무신사 스탠다드",
            category=Category.UPPER,
            price=29000,
            image_url="https://via.placeholder.com/300x400?text=Cotton+Tee",
            style_tags=["캐주얼", "베이직", "오버핏"],
        ),
        Item(
            id="item_002",
            name="스트라이프 옥스포드 셔츠",
            brand="무신사 스탠다드",
            category=Category.UPPER,
            price=45000,
            image_url="https://via.placeholder.com/300x400?text=Oxford+Shirt",
            style_tags=["클래식", "포멀", "스트라이프"],
        ),
        Item(
            id="item_003",
            name="그래픽 프린트 후드",
            brand="커버낫",
            category=Category.UPPER,
            price=79000,
            image_url="https://via.placeholder.com/300x400?text=Graphic+Hood",
            style_tags=["스트릿", "캐주얼", "그래픽"],
        ),
        Item(
            id="item_004",
            name="베이직 니트 스웨터",
            brand="디스이즈네버댓",
            category=Category.UPPER,
            price=89000,
            image_url="https://via.placeholder.com/300x400?text=Knit+Sweater",
            style_tags=["미니멀", "베이직", "니트"],
        ),
        Item(
            id="item_005",
            name="빈티지 워싱 티셔츠",
            brand="스투시",
            category=Category.UPPER,
            price=65000,
            image_url="https://via.placeholder.com/300x400?text=Vintage+Tee",
            style_tags=["스트릿", "빈티지", "워싱"],
        ),
        
        # 하의 (LOWER)
        Item(
            id="item_006",
            name="와이드 데님 팬츠",
            brand="무신사 스탠다드",
            category=Category.LOWER,
            price=59000,
            image_url="https://via.placeholder.com/300x400?text=Wide+Denim",
            style_tags=["캐주얼", "와이드", "데님"],
        ),
        Item(
            id="item_007",
            name="슬림핏 치노 팬츠",
            brand="무신사 스탠다드",
            category=Category.LOWER,
            price=49000,
            image_url="https://via.placeholder.com/300x400?text=Chino+Pants",
            style_tags=["클래식", "슬림", "치노"],
        ),
        Item(
            id="item_008",
            name="카고 조거 팬츠",
            brand="커버낫",
            category=Category.LOWER,
            price=69000,
            image_url="https://via.placeholder.com/300x400?text=Cargo+Jogger",
            style_tags=["스트릿", "카고", "조거"],
        ),
        Item(
            id="item_009",
            name="트레이닝 스웻 팬츠",
            brand="디스이즈네버댓",
            category=Category.LOWER,
            price=75000,
            image_url="https://via.placeholder.com/300x400?text=Sweat+Pants",
            style_tags=["스포티", "캐주얼", "스웻"],
        ),
        Item(
            id="item_010",
            name="버뮤다 쇼츠",
            brand="스투시",
            category=Category.LOWER,
            price=55000,
            image_url="https://via.placeholder.com/300x400?text=Bermuda+Shorts",
            style_tags=["스트릿", "여름", "쇼츠"],
        ),
        
        # 아우터 (OUTER)
        Item(
            id="item_011",
            name="오버핏 블레이저",
            brand="무신사 스탠다드",
            category=Category.OUTER,
            price=129000,
            image_url="https://via.placeholder.com/300x400?text=Overfit+Blazer",
            style_tags=["클래식", "오버핏", "블레이저"],
        ),
        Item(
            id="item_012",
            name="MA-1 봄버 자켓",
            brand="커버낫",
            category=Category.OUTER,
            price=159000,
            image_url="https://via.placeholder.com/300x400?text=MA1+Bomber",
            style_tags=["스트릿", "밀리터리", "봄버"],
        ),
        Item(
            id="item_013",
            name="퀄팅 패딩 자켓",
            brand="디스이즈네버댓",
            category=Category.OUTER,
            price=189000,
            image_url="https://via.placeholder.com/300x400?text=Quilting+Padding",
            style_tags=["겨울", "패딩", "퀄팅"],
        ),
        Item(
            id="item_014",
            name="코치 자켓",
            brand="스투시",
            category=Category.OUTER,
            price=139000,
            image_url="https://via.placeholder.com/300x400?text=Coach+Jacket",
            style_tags=["스트릿", "캐주얼", "코치"],
        ),
        Item(
            id="item_015",
            name="트렌치 코트",
            brand="무신사 스탠다드",
            category=Category.OUTER,
            price=179000,
            image_url="https://via.placeholder.com/300x400?text=Trench+Coat",
            style_tags=["클래식", "포멀", "트렌치"],
        ),
        
        # 신발 (SHOES)
        Item(
            id="item_016",
            name="캔버스 스니커즈",
            brand="컨버스",
            category=Category.SHOES,
            price=75000,
            image_url="https://via.placeholder.com/300x400?text=Canvas+Sneakers",
            style_tags=["캐주얼", "클래식", "캔버스"],
        ),
        Item(
            id="item_017",
            name="러닝화",
            brand="뉴발란스",
            category=Category.SHOES,
            price=139000,
            image_url="https://via.placeholder.com/300x400?text=Running+Shoes",
            style_tags=["스포티", "러닝", "편안함"],
        ),
        Item(
            id="item_018",
            name="가죽 로퍼",
            brand="닥터마틴",
            category=Category.SHOES,
            price=189000,
            image_url="https://via.placeholder.com/300x400?text=Leather+Loafer",
            style_tags=["클래식", "포멀", "가죽"],
        ),
        Item(
            id="item_019",
            name="에어맥스 스니커즈",
            brand="나이키",
            category=Category.SHOES,
            price=179000,
            image_url="https://via.placeholder.com/300x400?text=Airmax+Sneakers",
            style_tags=["스포티", "스트릿", "에어맥스"],
        ),
        Item(
            id="item_020",
            name="첼시 부츠",
            brand="닥터마틴",
            category=Category.SHOES,
            price=219000,
            image_url="https://via.placeholder.com/300x400?text=Chelsea+Boots",
            style_tags=["클래식", "부츠", "가죽"],
        ),
    ]
    
    for item in sample_items:
        item_store.add_item(item)
    
    # 샘플 사용자 데이터
    sample_users = [
        User(
            id="user_001",
            name="캐주얼 러버",
            preferred_brands=["무신사 스탠다드", "커버낫"],
            preferred_styles=["캐주얼", "스트릿"],
            preferred_categories=["upper", "lower"],
        ),
        User(
            id="user_002",
            name="클래식 맨",
            preferred_brands=["무신사 스탠다드", "닥터마틴"],
            preferred_styles=["클래식", "포멀"],
            preferred_categories=["outer", "shoes"],
        ),
        User(
            id="user_003",
            name="스트릿 보이",
            preferred_brands=["스투시", "커버낫", "나이키"],
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
    
    print(f"✅ Loaded {len(sample_items)} items and {len(sample_users)} users")

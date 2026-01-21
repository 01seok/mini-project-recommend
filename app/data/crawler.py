"""
무신사 크롤러

실제 상품 데이터를 크롤링하여 추천 시스템 테스트에 활용
"""

import httpx
import json
import re
import time
import random
from typing import List, Dict, Optional
from pathlib import Path
from bs4 import BeautifulSoup

# 카테고리 코드 매핑
CATEGORY_CODES = {
    "001": "upper",      # 상의
    "002": "outer",      # 아우터  
    "003": "lower",      # 하의
    "020": "shoes",      # 신발
    "004": "accessory",  # 가방
}


class MusinsaCrawler:
    """무신사 상품 크롤러"""
    
    BASE_URL = "https://www.musinsa.com"
    
    def __init__(self, delay_range: tuple = (1.0, 2.0)):
        self.delay_range = delay_range
        self.client = httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            },
            timeout=30.0,
            follow_redirects=True
        )
    
    def _delay(self):
        """요청 간 딜레이"""
        time.sleep(random.uniform(*self.delay_range))
    
    def _extract_next_data(self, html: str) -> Optional[Dict]:
        """__NEXT_DATA__ JSON 추출"""
        soup = BeautifulSoup(html, 'lxml')
        script = soup.find('script', id='__NEXT_DATA__')
        if script and script.string:
            try:
                return json.loads(script.string)
            except json.JSONDecodeError:
                pass
        return None
    
    def _parse_products_from_page(self, html: str, category: str) -> List[Dict]:
        """페이지 HTML에서 상품 정보 추출"""
        products = []
        
        # __NEXT_DATA__ 에서 추출 시도
        next_data = self._extract_next_data(html)
        if next_data:
            products.extend(self._parse_from_next_data(next_data, category))
        
        # 추가로 HTML에서 직접 파싱
        soup = BeautifulSoup(html, 'lxml')
        
        # 상품 링크 패턴: /products/{goods_no}
        product_links = soup.find_all('a', href=re.compile(r'/products/\d+'))
        
        seen_ids = {p.get('id') for p in products}
        
        for link in product_links:
            match = re.search(r'/products/(\d+)', link.get('href', ''))
            if not match:
                continue
            
            product_id = match.group(1)
            if product_id in seen_ids:
                continue
            
            # 부모 요소에서 정보 추출
            card = link.find_parent(['div', 'li', 'article'])
            if not card:
                continue
            
            text_content = card.get_text(separator='\n', strip=True)
            lines = [l.strip() for l in text_content.split('\n') if l.strip()]
            
            # 가격 추출
            price_match = re.search(r'([\d,]+)원', text_content)
            price = int(price_match.group(1).replace(',', '')) if price_match else 0
            
            # 이미지 URL 추출
            img = card.find('img')
            image_url = ""
            if img:
                image_url = img.get('src') or img.get('data-src', '')
            
            # 브랜드와 상품명 추출 (보통 첫 줄이 브랜드)
            brand = lines[0] if lines else "Unknown"
            name = lines[1] if len(lines) > 1 else f"Product {product_id}"
            
            products.append({
                'id': product_id,
                'name': name[:100],  # 길이 제한
                'brand': brand[:50],
                'category': category,
                'price': price,
                'image_url': image_url,
                'style_tags': [],
            })
            seen_ids.add(product_id)
        
        return products
    
    def _parse_from_next_data(self, data: Dict, category: str) -> List[Dict]:
        """__NEXT_DATA__ JSON에서 상품 파싱"""
        products = []
        
        def find_products(obj, depth=0):
            if depth > 10:
                return
            
            if isinstance(obj, dict):
                # 상품 객체 패턴 검출
                if 'goodsNo' in obj or 'goods_no' in obj:
                    product = self._parse_product_object(obj, category)
                    if product:
                        products.append(product)
                else:
                    for v in obj.values():
                        find_products(v, depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    find_products(item, depth + 1)
        
        find_products(data)
        return products
    
    def _parse_product_object(self, obj: Dict, category: str) -> Optional[Dict]:
        """상품 객체 파싱"""
        product_id = str(obj.get('goodsNo') or obj.get('goods_no') or obj.get('goodsNumber', ''))
        if not product_id:
            return None
        
        name = obj.get('goodsName') or obj.get('goods_name') or obj.get('name', f'Product {product_id}')
        brand = obj.get('brandName') or obj.get('brand_name') or obj.get('brand', 'Unknown')
        
        # 가격 처리
        price = obj.get('price') or obj.get('goodsPrice') or obj.get('normalPrice') or 0
        if isinstance(price, str):
            price = int(re.sub(r'[^\d]', '', price) or 0)
        
        # 이미지 URL
        image_url = obj.get('imageUrl') or obj.get('image_url') or obj.get('thumbnail', '')
        if image_url and not image_url.startswith('http'):
            image_url = f"https://image.msscdn.net{image_url}"
        
        return {
            'id': product_id,
            'name': str(name)[:100],
            'brand': str(brand)[:50],
            'category': category,
            'price': int(price),
            'image_url': image_url,
            'style_tags': [],
        }
    
    def crawl_category(self, category_code: str, limit: int = 100) -> List[Dict]:
        """카테고리별 상품 크롤링"""
        products = []
        category = CATEGORY_CODES.get(category_code, "upper")
        page = 1
        
        while len(products) < limit:
            url = f"{self.BASE_URL}/categories/item/{category_code}?gf=A&page={page}"
            print(f"  Crawling: {url}")
            
            try:
                response = self.client.get(url)
                if response.status_code != 200:
                    print(f"  Error: {response.status_code}")
                    break
                
                new_products = self._parse_products_from_page(response.text, category)
                
                if not new_products:
                    print(f"  No more products found on page {page}")
                    break
                
                # 중복 제거
                existing_ids = {p['id'] for p in products}
                for p in new_products:
                    if p['id'] not in existing_ids and len(products) < limit:
                        products.append(p)
                        existing_ids.add(p['id'])
                
                print(f"  Found {len(new_products)} products, total: {len(products)}")
                
                page += 1
                self._delay()
                
            except Exception as e:
                print(f"  Error crawling page {page}: {e}")
                break
        
        return products[:limit]
    
    def crawl(self, limit: int = 1000) -> List[Dict]:
        """
        전체 크롤링
        
        각 카테고리에서 균등하게 크롤링
        """
        products = []
        per_category = limit // len(CATEGORY_CODES) + 1
        
        print(f"🕷️ Starting Musinsa crawl (target: {limit} products)")
        print(f"   Crawling ~{per_category} per category")
        
        for code, cat_name in CATEGORY_CODES.items():
            print(f"\n📦 Category: {cat_name} ({code})")
            cat_products = self.crawl_category(code, per_category)
            products.extend(cat_products)
            print(f"   ✅ Got {len(cat_products)} products from {cat_name}")
            
            if len(products) >= limit:
                break
        
        # 중복 제거 및 제한
        seen = set()
        unique = []
        for p in products:
            if p['id'] not in seen:
                seen.add(p['id'])
                unique.append(p)
        
        result = unique[:limit]
        print(f"\n🎉 Total: {len(result)} unique products crawled")
        return result
    
    def save_to_file(self, products: List[Dict], filepath: str):
        """JSON 파일로 저장"""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Saved {len(products)} products to {filepath}")
    
    def close(self):
        """클라이언트 종료"""
        self.client.close()


def main():
    """크롤링 실행"""
    crawler = MusinsaCrawler(delay_range=(1.0, 1.5))
    
    try:
        products = crawler.crawl(limit=1000)
        
        # 저장
        output_path = Path(__file__).parent / "musinsa_products.json"
        crawler.save_to_file(products, str(output_path))
        
        # 통계 출력
        print("\n📊 Statistics:")
        categories = {}
        brands = {}
        for p in products:
            cat = p.get('category', 'unknown')
            brand = p.get('brand', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
            brands[brand] = brands.get(brand, 0) + 1
        
        print(f"   Categories: {categories}")
        print(f"   Unique brands: {len(brands)}")
        
    finally:
        crawler.close()


if __name__ == "__main__":
    main()

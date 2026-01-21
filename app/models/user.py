"""
사용자 모델
"""

from pydantic import BaseModel
from typing import List, Optional


class User(BaseModel):
    """사용자 정보"""
    id: str
    name: str
    preferred_brands: List[str] = []  # 선호 브랜드 (In-Network 소싱용)
    preferred_styles: List[str] = []  # 선호 스타일
    preferred_categories: List[str] = []  # 선호 카테고리

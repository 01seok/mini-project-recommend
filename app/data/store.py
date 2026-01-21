"""
In-Memory 데이터 저장소

실제 서비스에서는 DB(MongoDB, Redis 등)를 사용하지만,
미니 프로젝트에서는 간단한 In-Memory 저장소 사용
"""

from typing import Dict, List, Optional
from datetime import datetime
from app.models.item import Item
from app.models.user import User
from app.models.engagement import Engagement


class ItemStore:
    """상품 저장소"""
    
    def __init__(self):
        self._items: Dict[str, Item] = {}
    
    def add_item(self, item: Item) -> None:
        self._items[item.id] = item
    
    def get_item(self, item_id: str) -> Optional[Item]:
        return self._items.get(item_id)
    
    def get_all_items(self) -> List[Item]:
        return list(self._items.values())
    
    def clear(self) -> None:
        self._items.clear()


class UserStore:
    """사용자 저장소"""
    
    def __init__(self):
        self._users: Dict[str, User] = {}
    
    def add_user(self, user: User) -> None:
        self._users[user.id] = user
    
    def get_user(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)
    
    def get_all_users(self) -> List[User]:
        return list(self._users.values())


class EngagementStore:
    """
    사용자 행동 기록 저장소
    
    X 알고리즘의 User Action Sequence 저장
    """
    
    def __init__(self):
        self._engagements: Dict[str, List[Engagement]] = {}  # user_id -> engagements
    
    def add_engagement(self, engagement: Engagement) -> None:
        user_id = engagement.user_id
        if user_id not in self._engagements:
            self._engagements[user_id] = []
        self._engagements[user_id].append(engagement)
        
        # 최근 100개만 유지 (on_wear의 Redis ZSET 방식과 유사)
        self._engagements[user_id] = self._engagements[user_id][-100:]
    
    def get_user_history(self, user_id: str) -> List[Engagement]:
        return self._engagements.get(user_id, [])
    
    def clear_user_history(self, user_id: str) -> None:
        if user_id in self._engagements:
            self._engagements[user_id] = []


# 전역 저장소 인스턴스
item_store = ItemStore()
user_store = UserStore()
engagement_store = EngagementStore()

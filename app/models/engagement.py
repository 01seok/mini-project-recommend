"""
사용자 행동(Engagement) 모델

X 알고리즘의 User Action Sequence에 해당
"""

from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime


class ActionType(str, Enum):
    """행동 유형"""
    LIKE = "like"
    CLICK = "click"
    ADD_TO_CART = "add_to_cart"
    PURCHASE = "purchase"
    SHARE = "share"
    NOT_INTERESTED = "not_interested"
    HIDE = "hide"


class Engagement(BaseModel):
    """
    사용자 행동 기록
    
    X 알고리즘의 engagement history에 해당
    """
    user_id: str
    item_id: str
    action_type: ActionType
    timestamp: datetime = datetime.now()


class EngagementRequest(BaseModel):
    """행동 기록 API 요청"""
    user_id: str
    item_id: str
    action_type: ActionType

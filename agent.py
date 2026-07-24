import json
import os
from typing import List, Dict, Any
from pydantic import BaseModel, Field


class MenuItem(BaseModel):
    id: int
    name: str
    category: str
    price: float
    tags: List[str]
    image: str = ""


class OrderItem(BaseModel):
    item: MenuItem
    quantity: int


class Order(BaseModel):
    items: List[OrderItem] = Field(default_factory=list)

    @property
    def total_price(self) -> float:
        return sum(order_item.item.price * order_item.quantity for order_item in self.items)


class menumindAIAgent:
    """Core AI Backend Engine for menumind AI"""

    def __init__(self, menu_filepath: str):
        self.menu: List[MenuItem] = self._load_menu(menu_filepath)

    def _load_menu(self, filepath: str) -> List[MenuItem]:
        if not os.path.exists(filepath):
            return []
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [MenuItem(**item) for item in data]

    def get_all_menu_items(self) -> List[MenuItem]:
        return self.menu

    def recommend_items(self, user_preference: str) -> List[MenuItem]:
        """Filters menu items based on natural language preferences."""
        if not user_preference.strip():
            return self.menu

        keywords = user_preference.lower().split()
        recommendations = []

        for item in self.menu:
            match_score = 0
            searchable_text = f"{item.name.lower()} {item.category.lower()} {' '.join(item.tags)}"
            for kw in keywords:
                if kw in searchable_text:
                    match_score += 1
            if match_score > 0:
                recommendations.append((match_score, item))

        recommendations.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in recommendations]
from dataclasses import dataclass
from typing import Optional


@dataclass
class Product:
    id: str
    name: str
    brand: Optional[str]
    price: str
    category_0: Optional[str]
    category_1: Optional[str]
    category_2: Optional[str]
    category_3: Optional[str]

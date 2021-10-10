from dataclasses import dataclass


@dataclass
class Product:
    id: str
    name: str
    category_path: str  # IDEA: split in levels
    price: str
    currency: str
    brand: str

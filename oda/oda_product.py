from dataclasses import dataclass


@dataclass
class Product:
    id: str
    name: str
    # description: str
    category_path: str
    price: str
    currency: str
    brand: str

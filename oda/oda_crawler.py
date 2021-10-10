import re
from typing import Optional

from bs4 import BeautifulSoup

from crawler import Crawler
from frontier import Frontier
from oda.oda_product import Product


class OdaCrawler(Crawler):
    VISIT_RE = re.compile(r"^https://oda.com/no/(products|categories)/(\d+-.+)?$", flags=re.IGNORECASE)
    COLLECT_RE = re.compile(r"^https://oda.com/no/products/\d+-.+", flags=re.IGNORECASE)

    def __init__(self, url: str, max_visits: int, frontier: Frontier = None, visited: set[str] = None,
                 products: list[Product] = None):
        super().__init__(url, max_visits, frontier, visited)
        if products is None:
            products = []
        self.products = products

    def should_visit(self, url: str) -> bool:
        if not self.VISIT_RE.match(url):
            return False

        # from https://oda.com/robots.txt (TODO: fetch dynamically )
        disallow_list = [
            "/handlekurv/partial/",
            "/handlekurv/products/",
            "/handlekurv/toggle/",
            "/handlelister/ajax/0/products/",
            "/handlelister/ajax/new/",
            "/pakke/",
            "/sok/boost/",
            "/utlevering/ajax/delivery-availability/",
        ]

        for path in disallow_list:
            if url.startswith(f"https://oda.com{path}"):
                return False

        return True

    def should_prioritize_visit(self, url: str) -> bool:
        return self.COLLECT_RE.match(url) is not None

    def should_collect(self, url: str, status_code: int) -> bool:
        return self.COLLECT_RE.match(url) is not None

    def collect(self, url: str, html: Optional[BeautifulSoup], status_code: int):
        if html is None:
            return

        last_category_link = html.select_one(f".breadcrumb :last-of-type > a[itemprop=url]")

        category_levels = []
        if last_category_link is not None:
            category_path = last_category_link.attrs.get("href")
            category_levels = category_path.split("/")[1:-1] if category_path is not None else []
            if "categories" in category_levels:
                category_levels.remove("categories")

        product = Product(
            id=tag.attrs.get("data-product") if (tag := html.select_one(f"[data-product]")) else None,
            name=tag.get_text(" ", strip=True) if (tag := html.select_one(f"h1 [itemprop=name]")) else None,
            brand=tag.get_text(" ", strip=True) if (tag := html.select_one(f"[itemprop=brand]")) else None,
            price=tag.attrs.get("content") if (tag := html.select_one(f"[itemprop=price]")) else None,
            category_0=category_levels[0] if len(category_levels) > 0 else None,
            category_1=category_levels[1] if len(category_levels) > 1 else None,
            category_2=category_levels[2] if len(category_levels) > 2 else None,
            category_3=category_levels[3] if len(category_levels) > 3 else None
        )

        self.products.append(product)

    def print_stats(self):
        super().print_stats()
        print(f"collected: {len(self.products)} products")

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
                 collected: list[Product] = None):
        super().__init__(url, max_visits, frontier, visited)
        if collected is None:
            collected = []
        self.collected = collected

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

        product = Product(
            id=tag.attrs.get('data-product') if (tag := html.select_one(f"[data-product]")) else None,
            name=tag.get_text(" ", strip=True) if (tag := html.select_one(f"h1 [itemprop=name]")) else None,
            category_path=tag.attrs.get('href') if (tag := html.select_one(f".breadcrumb :last-of-type > a[itemprop=url]")) else None,
            price=tag.attrs.get('content') if (tag := html.select_one(f"[itemprop=price]")) else None,
            currency=tag.attrs.get('content') if (tag := html.select_one(f"[itemprop=priceCurrency]")) else None,
            brand=tag.get_text(" ", strip=True) if (tag := html.select_one(f"[itemprop=brand]")) else None
        )

        self.collected.append(product)

    def print_stats(self):
        super().print_stats()
        print(f"collected: {len(self.collected)} products")

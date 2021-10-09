import re
from crawler import Crawler
from frontier import Frontier, InMemoryDequeFrontier, InMemorySetFrontier
from oda.oda_product import Product
from bs4 import BeautifulSoup


class OdaCrawler(Crawler):
    VISIT_RE = re.compile(r"^https://oda.com/no/(?:products|categories)/.*", flags=re.IGNORECASE)
    COLLECT_RE = re.compile(r"^https://oda.com/no/products/\d+-.+", flags=re.IGNORECASE)

    def __init__(self, url: str, max: int, frontier: Frontier=InMemorySetFrontier(),  visited: set[str]=set(), collected: list[Product]=[]):
        super().__init__(url, max=max, frontier=frontier, visited=visited)
        self.collected = collected
    
    def should_visit(self, url: str) -> bool:
        if not self.VISIT_RE.match(url):
            return False
        
        # TODO fetch dynamically from https://oda.com/robots.txt
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
            if path in url:
                return False
        
        return True
    
    def should_prioritize_visit(self, url: str) -> bool:
        return self.COLLECT_RE.match(url) is not None

    def should_collect(self, url: str, status_code: int) -> bool:
        return self.COLLECT_RE.match(url) is not None

    def collect(self, url: str, html: str, status_code: int) -> None:
        soup = BeautifulSoup(html, "html.parser") # TODO: optimize by moving 'out' the html parsing

        product = Product(
            id=tag.attrs.get('data-product') if (tag := soup.select_one(f"[data-product]")) else None,
            name=tag.get_text(" ", strip=True) if (tag := soup.select_one(f"h1 [itemprop=name]")) else None,
            # description=tag.get_text(" ", strip=True) if (tag := soup.select_one(f"[itemprop=description]")) else None,
            category_path=tag.attrs.get('href') if (tag := soup.select_one(f".breadcrumb :last-of-type > a[itemprop=url]")) else None,
            price=tag.attrs.get('content') if (tag := soup.select_one(f"[itemprop=price]")) else None,
            currency=tag.attrs.get('content') if (tag := soup.select_one(f"[itemprop=priceCurrency]")) else None,
            brand=tag.get_text(" ", strip=True) if (tag := soup.select_one(f"[itemprop=brand]")) else None
        )

        self.collected.append(product)

    def print_stats(self):
        super().print_stats()
        print(f"collected: {len(self.collected)} products")
    
   
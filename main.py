import csv
from dataclasses import asdict
from oda_crawler import OdaCrawler


def main():

    crawler = OdaCrawler("https://oda.com/no/products/", max=2000, collected=[])
    crawler.crawl()

    with open('oda_products.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id",
            "name",
            # "description",
            "category_path",
            "price",
            "currency",
            "brand"
        ])
        writer.writeheader()
        writer.writerows([asdict(p) for p in crawler.collected])
    
    print("DONE")
    print(f"visited: {len(crawler.visited)} pages")
    print(f"frontier: {len(crawler.frontier)} pages")
    print(f"collected: {len(crawler.collected)} products")


if __name__ == "__main__":
    main()

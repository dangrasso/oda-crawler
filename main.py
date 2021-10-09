import csv
import json
from datetime import datetime
from dataclasses import asdict, fields
from crawler import Crawler
from oda.oda_crawler import OdaCrawler
from oda.oda_product import Product


def main():
    start_time = datetime.now()
    collected_products: list[Product] = []
    crawler: Crawler = OdaCrawler("https://oda.com/no/products/", max=5, collected=collected_products)
    crawler.crawl()

    crawl_end_time = datetime.now()
    print(f"DONE crawling in {crawl_end_time - start_time}")

    print(f"Saving crawling results...")    

    with open(f'oda_products_{start_time:%Y%m%d-%H%M}.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[f.name for f in fields(Product)])
        writer.writeheader()
        writer.writerows([asdict(p) for p in collected_products])
    
    # IDEA: allow saving and restoring state
    with open(f'oda_frontier_{start_time:%Y%m%d-%H%M}.json', 'w', encoding='UTF8', newline='') as f:
        f.write(json.dumps(list(crawler.frontier)))

    with open(f'oda_visited_{start_time:%Y%m%d-%H%M}.json', 'w', encoding='UTF8', newline='') as f:
        f.write(json.dumps(list(crawler.visited)))

    end_time = datetime.now()
    
    print(f"DONE in {end_time - crawl_end_time}")
    crawler.print_stats()

if __name__ == "__main__":
    main()

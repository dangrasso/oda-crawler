import csv
import json
import signal
import sys
from dataclasses import asdict, fields
from datetime import datetime

from oda.oda_crawler import OdaCrawler
from oda.oda_product import Product


def save_state(frontier, visited, collected):
    now = datetime.now()

    with open(f'oda_frontier_{now:%Y%m%d-%H%M}.json', 'w', encoding='UTF8') as file:
        file.write(json.dumps(list(frontier), indent=2))
        print(f'Saved frontier: {file.name}')

    with open(f'oda_visited_{now:%Y%m%d-%H%M}.json', 'w', encoding='UTF8') as file:
        file.write(json.dumps(list(visited), indent=2))
        print(f'Saved visited: {file.name}')

    with open(f'oda_products_{now:%Y%m%d-%H%M}.csv', 'w', encoding='UTF8') as file:
        writer = csv.DictWriter(file, fieldnames=[field.name for field in fields(Product)])
        writer.writeheader()
        writer.writerows([asdict(product) for product in collected])
        print(f'Saved collected: {file.name}')


def main():
    crawler = OdaCrawler("https://oda.com/no/products/", max_visits=10000)
    # IDEA: allow loading status

    def on_interrupt(*args):
        print('\nInterrupted! Saving state before exiting...')
        save_state(frontier=crawler.frontier, visited=crawler.visited, collected=crawler.collected)
        sys.exit(0)

    signal.signal(signal.SIGINT, on_interrupt)

    start = datetime.now()
    crawler.crawl()
    end = datetime.now()
    print(f"DONE crawling in {(end - start)}")
    crawler.print_stats()

    print(f"Saving crawling results...")
    save_state(frontier=crawler.frontier, visited=crawler.visited, collected=crawler.collected)


if __name__ == "__main__":
    main()

import os
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from oda.oda_crawler import OdaCrawler
from oda.oda_product import Product

FIXTURES_PATH = Path(os.path.dirname(os.path.realpath(__file__))) / "fixtures"


class UtilTest(unittest.TestCase):
    def test_collect_none(self):
        products = []
        crawler = OdaCrawler("dummy.url", 1, products=products)

        crawler.collect("url", None, 200)

        self.assertEqual(0, len(products))

    def test_collect_product(self):
        products = []
        crawler = OdaCrawler("dummy.url", 1, products=products)
        content = BeautifulSoup(open(f"{FIXTURES_PATH}/product_chicken.html"), "html.parser")
        expected_product = Product(
            id="31885",
            name="Økologisk Hel kylling ca. 2,4 kg",
            brand="Hovelsrud Gård",
            price="386.60",
            category_0="no",
            category_1="488-mathall",
            category_2="489-kjottdisken",
            category_3=None
        )

        crawler.collect("url", content, 200)

        self.assertEqual(1, len(products))
        self.assertEqual(expected_product, products[0])

    def test_collect_product__with_no_categories(self):
        products = []
        crawler = OdaCrawler("dummy.url", 1, products=products)
        content = BeautifulSoup(open(f"{FIXTURES_PATH}/product_no_categories_nellik.html"), "html.parser")
        expected_product = Product(
            id="6250",
            name="Nellik Malt 10 g",
            brand="Toro",
            price="7.40",
            category_0=None,
            category_1=None,
            category_2=None,
            category_3=None
        )

        crawler.collect("url", content, 200)

        self.assertEqual(1, len(products))
        self.assertEqual(expected_product, products[0])


if __name__ == "__main__":
    unittest.main()

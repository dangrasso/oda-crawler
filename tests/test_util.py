import unittest

from util import get_base_url, to_absolute_url


class UtilTest(unittest.TestCase):
    def test_get_base_url(self):
        self.assertEqual("https://oda.com",         get_base_url("https://oda.com/no/products/123"))
        self.assertEqual("http://example.com:8080", get_base_url("http://example.com:8080/"))

    def test_to_absolute_url(self):
        base_url = "https://oda.com"
        self.assertEqual("https://oda.com/test/1?q=v",  to_absolute_url(base_url, "/test/1?q=v"))
        self.assertEqual("https://oda.com/test/other",  to_absolute_url(base_url, "./test/some/../other"))
        self.assertEqual("https://oda.com",             to_absolute_url(base_url, ""))

    def test_to_absolute_url__deal_with_slashes(self):
        base_url = "https://oda.com"
        self.assertEqual("https://oda.com/test", to_absolute_url(base_url, "/test"))
        self.assertEqual("https://oda.com/test", to_absolute_url(base_url, "test"))
        self.assertEqual("https://oda.com/test", to_absolute_url(f"{base_url}/", "/test"))
        self.assertEqual("https://oda.com/test", to_absolute_url(f"{base_url}/", "test"))

    def test_to_absolute_url__when_already_absolute(self):
        base_url = "https://oda.com"
        self.assertEqual("https://other.com/test",  to_absolute_url(base_url, "https://other.com/test"))
        self.assertEqual("https://oda.com/test",    to_absolute_url(base_url, "https://oda.com/test"))
        self.assertEqual("https://oda.com/test",    to_absolute_url("",       "https://oda.com/test"))


if __name__ == "__main__":
    unittest.main()

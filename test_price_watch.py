import unittest

from price_watch import check_product, extract_price

BOOK_HTML = """
<html><body>
<article class="product_pod">
  <h1>A Light in the Attic</h1>
  <p class="price_color">&pound;51.77</p>
</article>
</body></html>
"""


class ExtractPriceTest(unittest.TestCase):
    def test_book_page(self):
        self.assertEqual(extract_price(BOOK_HTML), 51.77)

    def test_plain_currency(self):
        self.assertEqual(extract_price("<p>Only $19.99 today</p>"), 19.99)

    def test_no_price(self):
        self.assertIsNone(extract_price("<p>nothing for sale</p>"))


class CheckProductTest(unittest.TestCase):
    def fake_fetcher(self, url):
        return BOOK_HTML

    def test_records_history_and_no_alert_above_target(self):
        product = {"url": "http://example.test/book", "target": 40.0,
                   "history": []}
        price, alert = check_product("Book", product, fetcher=self.fake_fetcher)
        self.assertEqual(price, 51.77)
        self.assertFalse(alert)
        self.assertEqual(len(product["history"]), 1)

    def test_alert_at_or_below_target(self):
        product = {"url": "http://example.test/book", "target": 51.77,
                   "history": []}
        _, alert = check_product("Book", product, fetcher=self.fake_fetcher)
        self.assertTrue(alert)


if __name__ == "__main__":
    unittest.main()

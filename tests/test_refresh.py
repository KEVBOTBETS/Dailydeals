import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('refresh',Path(__file__).resolve().parents[1]/'scripts/refresh.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

class ExtractionTests(unittest.TestCase):
    def test_empty_page_never_creates_offer(self):
        self.assertEqual(r.official_deals({}),[])
    def test_parse_kfc_price_from_source(self):
        deals=r.official_deals({r.KFC:'$4.95 Popcorn Fill Up $9.99 Bucket for 1'})
        self.assertEqual([d['price'] for d in deals],[4.95,9.99])
    def test_changed_price_is_not_hardcoded(self):
        self.assertEqual(r.official_deals({r.KFC:'$5.95 Popcorn Fill Up'})[0]['price'],5.95)
    def test_no_fabricated_weekly_special(self):
        self.assertEqual(r.official_deals({r.KFC:'Tuesday Twosdays'}),[])
    def test_date_list_has_real_dates_and_weekday(self):
        previous=r.TODAY;r.TODAY='2026-11-10'
        try:
            d=r.official_deals({r.MCD:'FREE fries. Valid Nov 6, 13 & 20/26'})[0]
            self.assertEqual(d['days'],['Friday']);self.assertEqual(d['ends'],'2026-11-20')
            self.assertIsNone(d['price']) # Conditional freebie is not a zero-dollar meal.
        finally:r.TODAY=previous
    def test_expired_date_list_is_removed(self):
        previous=r.TODAY;r.TODAY='2026-12-01'
        try:self.assertEqual(r.official_deals({r.MCD:'FREE fries. Valid Nov 6, 13 & 20/26'}),[])
        finally:r.TODAY=previous
    def test_parser_ignores_script_prices(self):
        self.assertNotIn('9.99',r.plain('<script>$9.99</script><h1>Coupons</h1>'))

if __name__=='__main__':unittest.main()

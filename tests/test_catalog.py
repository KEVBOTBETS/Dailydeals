import unittest
from scripts import refresh as r
from scripts import catalog as c

class LocalEvidenceTests(unittest.TestCase):
    def test_local_price_requires_branch_address(self):
        self.assertEqual(c.local_deals({c.BIG:'Falafel Wrap Vegan $9.99'},r.deal,r.NOW,r.DAYS),[])
    def test_price_belongs_to_same_item(self):
        self.assertEqual(c.local_deals({c.BIG:'500 Rossland Falafel Wrap Vegan unavailable Chicken Wrap $11.99'},r.deal,r.NOW,r.DAYS)[0]['id'],'big-chicken')
    def test_local_price_is_extracted_and_linked_to_branch(self):
        d=c.local_deals({c.BIG:'500 Rossland Falafel Wrap Vegan $10.99'},r.deal,r.NOW,r.DAYS)[0]
        self.assertEqual(d['price'],10.99);self.assertEqual(d['verification'],'branch-menu');self.assertEqual(d['branchIds'],['bigbites-rossland'])
    def test_pita_deli_is_not_listed_on_sunday(self):
        d=c.local_deals({c.PITA:'1600 Champlain Vegetarian $11.95'},r.deal,r.NOW,r.DAYS)[0]
        self.assertNotIn('Sunday',d['days'])
    def test_chain_address_does_not_prove_price(self):
        b=next(b for b in c.branch_records({'https://locations.wendys.com/canada/on/oshawa/323-king-st-w':'323 King'},r.NOW) if b['id']=='wendys-king')
        self.assertTrue(b['addressVerified']);self.assertFalse(b['hasPricedMenu'])
    def test_split_animated_osmows_price_and_weekdays(self):
        text='$12 $12 $12 99 99 PLUS TAX Monday Chicken Shawarma Wrap Box Tuesday Beef Shawarma OzBox Wednesday Chicken Shawarma Poutine'
        ds=c.chain_additions({c.OSMOW:text},r.deal,r.DAYS)
        self.assertEqual([d['price'] for d in ds],[12.99]*3)
        self.assertEqual([d['days'] for d in ds],[['Monday'],['Tuesday'],['Wednesday']])
    def test_unsupported_price_does_not_promote_day_special(self):
        self.assertEqual(c.chain_additions({c.OSMOW:'$7.99 unrelated menu Monday Chicken Shawarma Wrap Box'},r.deal,r.DAYS),[])
    def test_conditional_freebie_exposes_minimum_spend(self):
        d=c.enrich([r.deal('mc-fries','McDonald’s','Free fries','',None,r.MCD)])[0]
        self.assertEqual(d['price'],0);self.assertEqual(d['minimumSpend'],3);self.assertTrue(d['requirements']['registration'])
    def test_coupon_lead_needs_exact_merchant_price(self):
        deals=[r.deal('one','Big Bites Shawarma','Falafel wrap','',9.99,c.BIG)]
        lead={'title':'Big Bites Shawarma Falafel wrap $8.99'}
        self.assertEqual(c.match_leads([lead],deals)[0]['status'],'unverified')
        lead={'title':'Big Bites Shawarma Falafel wrap $9.99'}
        self.assertEqual(c.match_leads([lead],deals)[0]['status'],'merchant-match')
    def test_requested_restaurants_have_official_destinations(self):
        brands={x[1] for x in c.EXTRA_DESTINATIONS}
        self.assertTrue({'Thai Express','Booster Juice','barBurrito','Starbucks'}<=brands)

if __name__=='__main__':unittest.main()

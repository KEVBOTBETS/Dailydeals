#!/usr/bin/env python3
"""Fetch Canadian restaurant offer pages and coupon RSS feeds. No keys required.

Only explicit, bounded official-source rules become priced offers. New internet
finds stay unverified leads; never infer a branch's participation from a town.
"""
import argparse
import concurrent.futures
import datetime as dt
import html
import gzip
import zlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import urllib.request
import urllib.error
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo
try:
    import catalog
    import image_offers
except ImportError:
    from scripts import catalog
    from scripts import image_offers

ROOT = Path(__file__).resolve().parents[1]
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
NOW = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
TODAY = dt.datetime.now(ZoneInfo('America/Toronto')).date().isoformat()
MCD = 'https://www.mcdonalds.com/ca/en-ca.html'
PROMISE = 'https://www.mcdonalds.com/ca/en-ca/newsroom/article/McDonald-s-Canada-Announces-One-Year-Price-Promise-on--5-McValue--Meals-and--1-small-McCaf---Coffee-.html'
KFC = 'https://www.kfc.ca/menu/kfcca-exclusive-offers'
WENDYS = 'https://www.wendys.com/en-ca'
HARVEYS = 'https://www.harveys.ca/en/coupons.html'
SOURCES = [
    ('McDonald’s current offers', MCD), ('McDonald’s price promise', PROMISE),
    ('KFC online offers', KFC), ('KFC Ontario coupons', 'https://www.kfc.ca/coupons'),
    ('Wendy’s Canada', WENDYS), ('Harvey’s coupons', HARVEYS),
    ('Harvey’s deals', 'https://www.harveys.ca/en/deals.html'),
    ('Subway Canada', 'https://www.subway.com/en-ca/'),
    ('Mary Brown’s', 'https://marybrowns.com/'),
    ('Pizza Pizza', 'https://www.pizzapizza.ca/for-you/'),
    ('A&W Canada', 'https://web.aw.ca/en/our-menu'),
    ('Tim Hortons', 'https://www.timhortons.ca/offers'),
    ('SmartCanucks RSS', 'https://smartcanucks.ca/feed/'),
    ('SaveaLoonie RSS', 'https://www.savealoonie.com/feed/'),
]
SOURCES = list(dict.fromkeys(SOURCES + catalog.EXTRA_SOURCES))
SOURCES.append(('Thai Express daily Discovery Menu','https://thaiexpress.ca/discovery-menu-week/'))

class TextParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.skip = 0; self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.skip = max(0, self.skip-1)
    def handle_data(self, text):
        if not self.skip: self.parts.append(text)

def plain(raw):
    p = TextParser(); p.feed(raw)
    return re.sub(r'\s+', ' ', html.unescape(' '.join(p.parts))).strip()

def fetch(source):
    name, url = source
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'DurhamDailyDealFinder/1.0 (+https://github.com/KEVBOTBETS/Dailydeals)', 'Accept-Language': 'en-CA,en;q=0.9', 'Accept-Encoding':'identity'})
        with urllib.request.urlopen(req, timeout=22) as response:
            body=response.read(3_000_000)
            encoding=response.headers.get('Content-Encoding','').lower()
            if encoding=='gzip':body=gzip.decompress(body)
            elif encoding=='deflate':body=zlib.decompress(body)
            elif encoding not in ('','identity'):raise ValueError('Unsupported compressed response')
            raw = body.decode('utf-8')
        text = plain(raw)
        if len(text) < 80 or re.search(r'(just a moment|access denied|verify you are human)', text[:500], re.I):
            raise ValueError('Empty, JavaScript-only or blocked response')
        return dict(name=name, url=url, ok=True, checkedAt=NOW, raw=raw, text=text)
    except (OSError, ValueError, urllib.error.URLError, zlib.error) as error:
        return dict(name=name, url=url, ok=False, checkedAt=NOW, error=str(error)[:160], text='', raw='')

def deal(id, brand, title, description, price, url, **extra):
    result = dict(id=id, brand=brand, title=title, description=description, price=price,
                  url=url, days=DAYS[:], kind='meal', redemption='Pickup / in-store',
                  priceLabel='before tax', icon='🍔', color='#efe7d2', checkedAt=NOW,
                  terms='Participating Canadian restaurants. Confirm the offer and availability at your chosen Durham branch. Delivery, upgrades and taxes can cost extra.')
    result.update(extra)
    return result

def official_deals(pages):
    found=[]
    text = pages.get(PROMISE, '')
    # The dated 2026 price guarantee must expire, even if the old article stays online.
    if '01-13-2026' in text and re.search(r'priced at\s*\$5', text, re.I):
        for id,title,description,redemption,icon in [
            ('mcvalue-lunch','McValue lunch & dinner meal','Choose a McDouble, Junior Chicken or Chicken Snack Wrap meal with small fries and a small drink.','Lunch / dinner','🍔'),
            ('mcvalue-breakfast','McValue breakfast meal','Selected breakfast sandwiches or a bagel, with a hash brown and small coffee.','Before 11 a.m.','🥯')]:
            found.append(deal(id,'McDonald’s',title,description,5,PROMISE,redemption=redemption,icon=icon,ends='2027-01-12',terms='2026 one-year price promise announced January 13. Breakfast until 11 a.m. Prices before tax; not available through delivery. Product availability varies by restaurant. Confirm at your local branch.'))
    if '01-13-2026' in text and re.search(r'\$1\s+Small McCaf',text,re.I):
        found.append(deal('mc-coffee','McDonald’s','Small McCafé coffee','An everyday low-cost coffee stop. No minimum purchase stated in the price promise.',1,PROMISE,icon='☕',ends='2027-01-12',terms='Small coffee only; 2026 price guarantee. Before tax; not available through delivery. Customizations may cost extra.'))
    text = pages.get(KFC,'')
    for id,pattern,title,description in [
        ('kfc-popcorn',r'\$(\d+\.\d{2})\s+Popcorn Fill Up','Popcorn Fill Up','Look for the Popcorn Fill Up in KFC’s exclusive online offers; choose your store to confirm contents and availability.'),
        ('kfc-bucket-one',r'\$(\d+\.\d{2})\s+Bucket for 1','Bucket for one','A solo bucket listed on KFC Canada’s menu. Select your local restaurant for the exact contents and price.')]:
        match=re.search(pattern,text,re.I)
        if match:found.append(deal(id,'KFC',title,description,float(match[1]),KFC,icon='🍗',color='#f4e0d6',redemption='Order online / pickup'))
    text = pages.get(WENDYS,'')
    # Only display this limited promotion while the explicit date and price still match.
    if re.search(r'\$8\.99 Canadian Meal Deal',text) and 'Only until November 15' in text:
        found.append(deal('wendys-canadian','Wendy’s','Canadian Meal Deal','A quarter-pound beef burger, Canadian fries, a Frosty and a drink. Ask for the Canadian Meal Deal.',8.99,WENDYS,icon='🍔',color='#f1ddd3',ends='2026-11-15',terms='Limited offer through November 15, 2026 at participating Canadian Wendy’s. Request the $8.99 Canadian Meal Deal. Upsizing and taxes extra.'))
    text = pages.get(MCD,'')
    # Date-list offers: retain explicit eligible dates, never turn a one-off into a weekly deal.
    specs=[('mc-fries','Free fries with a purchase','Get medium fries with a minimum $3 pre-tax purchase; a hash brown is offered before 11 a.m.',r'Valid Nov (6, 13 & 20)/26','FREE',None,'🍟'),
           ('mc-dessert','App dessert offer','A Snack Size McFlurry or Sundae offer in the McDonald’s app. Premium McFlurry flavours excluded.',r'Valid Nov (9, 16 & 23)/26','only $2',2,'🍦')]
    for id,title,desc,pattern,required,price,icon in specs:
        match=re.search(pattern,text,re.I)
        if match and required.lower() in text.lower():
            dates=['2026-11-'+d.zfill(2) for d in re.findall(r'\d+',match[1])]
            if max(dates)<TODAY: continue
            scheduled=list(dict.fromkeys(dt.date.fromisoformat(x).strftime('%A') for x in dates))
            found.append(deal(id,'McDonald’s',title,desc,price,MCD,days=scheduled,dates=dates,starts=min(dates),ends=max(dates),icon=icon,color='#f5e5cb',redemption='App + registration',priceLabel='before tax' if price else 'min. $3 purchase',terms='Only valid on '+', '.join(dates)+'. At participating Canadian restaurants. App registration required, one redemption per user; full terms in-app. Free fries requires at least $3 pre-tax spending.'))
    return [d for d in found if not d.get('ends') or d['ends']>=TODAY]

def destinations(pages):
    specs=[('mc-coupons','McDonald’s','App offers & rewards',MCD,'🍟','#f5e5cb','Sign in to the Canadian app and select your restaurant to see account-specific offers.'),
    ('kfc-coupons','KFC','Ontario printable coupons','https://www.kfc.ca/coupons','🍗','#f4e0d6','Choose Ontario on the official coupon page, then check the expiry and participating restaurants.'),
    ('harveys-coupons','Harvey’s','Coupon wallet & late-night deals',HARVEYS,'🍔','#ede6d7','Check the coupon wallet. Published late-night app offers begin after 8 p.m.; store hours vary.'),
    ('wendys-coupons','Wendy’s','Canadian offers & rewards',WENDYS,'🍔','#f1ddd3','Check the Canadian menu and your app account for current offers before ordering.'),
    ('subway-coupons','Subway','Rewards & sandwich offers','https://www.subway.com/en-ca/','🥪','#e8edd6','Check the Canadian site or app for the offer available at your local restaurant.'),
    ('mary-coupons','Mary Brown’s','Local menu & app offers','https://marybrowns.com/','🍗','#f2e4ca','Select Ontario and your local restaurant for current offers and app deals.'),
    ('pizza-coupons','Pizza Pizza','Pizza offers & ordering','https://www.pizzapizza.ca/for-you/','🍕','#f3e1ce','Explore official offers and compare pickup pricing for your selected store.'),
    ('tims-coupons','Tim Hortons','App offer check','https://www.timhortons.ca/offers','☕','#ece2d5','Open the Canadian app for personalized coupons. Prices and offers vary by account and restaurant.')]
    return [deal(id,brand,title,desc,None,url,kind='coupon',icon=icon,color=color,checkedAt=NOW if url in pages else None,redemption='Check website / app',terms='Coupon destination only: no particular discount or coupon code has been verified. Login, minimum spend, purchase limits and exclusions may apply. Confirm dates and your local branch in the app or website.') for id,brand,title,url,icon,color,desc in specs]

def healthier():
    return [deal('lighter-sub','Subway','Build a veg-packed smaller sub','Try a 6-inch sandwich, add vegetables and compare sauces. Check the price before adding extras.',None,'https://www.subway.com/en-ca/menunutrition/nutrition',kind='lighter',icon='🥪',color='#e3ead5',checkedAt=None,redemption='Menu idea',terms='A meal customization idea, not a verified discount or nutrition claim. The finished meal depends on bread, protein, sauces and portion. Compare the Canadian nutrition information and local menu price.'),
    deal('lighter-wendys','Wendy’s','Compare a chili-based lunch','Look at a small chili or a plain baked potato as an alternative to fries, if your store offers them. Compare price and portion.',None,'https://order.wendys.com/ca/en/national/menu',kind='lighter',icon='🥔',color='#e7eadc',checkedAt=None,redemption='Menu idea',terms='Not a discounted meal; local availability and pricing must be checked. Toppings, sodium and serving size affect the meal. Use the Canadian menu nutrition for the exact item.'),
    deal('lighter-harveys','Harvey’s','More garnish, simpler drink','Ask for extra vegetables from the garnish counter. Compare a smaller burger and water with a full combo.',None,'https://www.harveys.ca/en/nutrition.html',kind='lighter',icon='🥬',color='#e4ecd6',checkedAt=None,redemption='Menu idea',terms='A suggested swap, not a verified discount. Extra toppings may cost more. Check ingredients, allergens and sodium in the restaurant nutrition information.')]

def discover(results):
    leads=[];seen=set()
    food=re.compile(r"mcdonald|wendy|harvey|subway|kfc|mary brown|pizza|tim horton|a&w|burger king|popeye|taco bell|osmow|freshii|pita pit|fast food|restaurant|shawarma|thai express|booster juice|barburrito|starbucks|mucho burrito",re.I)
    for r in results:
        if 'RSS' not in r['name'] or not r['ok']: continue
        try: root=ET.fromstring(r['raw'])
        except ET.ParseError:continue
        for item in root.findall('.//item'):
            title=plain(item.findtext('title',''));link=item.findtext('link','')
            if not food.search(title) or link in seen or urlparse(link).scheme!='https': continue
            pub=item.findtext('pubDate','')
            if pub:
                try:
                    from email.utils import parsedate_to_datetime
                    published=parsedate_to_datetime(pub)
                    if published.tzinfo is None: published=published.replace(tzinfo=dt.timezone.utc)
                    if (dt.datetime.now(dt.timezone.utc)-published).days>14:continue
                except (ValueError,TypeError):continue
            # Never copy prices or coupon codes from discovery into verified offers.
            seen.add(link);leads.append(dict(title=title[:180],url=link,snippet='Canadian coupon-site lead. Check the original merchant, location, eligible dates and conditions.',foundAt=NOW,publishedAt=pub,query=r['name']))
    return leads[:18]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default=str(ROOT/'docs/data/deals.json'));args=parser.parse_args()
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: results=list(pool.map(fetch,SOURCES))
    pages={r['url']:r['text'] for r in results if r['ok']}
    target=Path(args.output)
    old={}
    if target.exists():
        try:old=json.loads(target.read_text())
        except (ValueError,OSError):pass
    poster_offers,poster_source=image_offers.thai_discovery({r['url']:r['raw'] for r in results if r['ok']},deal,NOW)
    offers=official_deals(pages)+catalog.local_deals(pages,deal,NOW,DAYS)+catalog.chain_additions(pages,deal,DAYS)+poster_offers
    # Preserve previously verified offers only during a short, labelled fetch failure.
    ids={d['id'] for d in offers}
    for d in old.get('deals',[]):
        if d.get('kind')!='meal' or d['id'] in ids:continue
        if d.get('posterUrl'):
            if not poster_source.get('error','').startswith('Poster source unavailable:'):continue
        elif d['url'] in pages:continue
        try:age=(dt.datetime.fromisoformat(NOW)-dt.datetime.fromisoformat(d['checkedAt'])).total_seconds()/86400
        except (ValueError,TypeError,KeyError):continue
        if age<=3 and (not d.get('ends') or d['ends']>=TODAY):
            d=dict(d,sourceUnavailable=True);offers.append(d)
    extra=[deal(id+'-coupons',brand,title,catalog.DESTINATION_NOTES.get(brand,'Open the official Canadian offer or local ordering page. Availability and account requirements vary.'),None,url,kind='coupon',icon=icon,checkedAt=NOW if url in pages else None,terms='No discount or code is guaranteed. Select your restaurant and inspect the current offer before ordering.') for id,brand,title,url,icon in catalog.EXTRA_DESTINATIONS]
    deals=catalog.enrich(offers+destinations(pages)+extra+healthier())
    leads=discover(results)+catalog.link_leads(results,NOW)
    unique={l['url']:l for l in leads}
    payload=dict(schemaVersion=2,generatedAt=NOW,timezone='America/Toronto',currency='CAD',region='Durham Region, Ontario',deals=deals,branches=catalog.branch_records(pages,NOW),leads=catalog.match_leads(list(unique.values()),deals),sources=[{k:v for k,v in r.items() if k not in ('text','raw')} for r in results]+[poster_source])
    target.parent.mkdir(parents=True,exist_ok=True)
    tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n');tmp.replace(target)
    print(f'Refreshed {len(offers)} published offers, {len(payload["leads"])} unverified leads; {len(pages)}/{len(SOURCES)} sources reachable.')
    if not offers: print('WARNING: No priced official offers verified. Coupon destinations remain available.')
    if not pages: raise SystemExit('No sources reachable: investigate network or source blocks.')

if __name__=='__main__': main()

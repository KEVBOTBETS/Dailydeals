"""Curated official Durham sources, branch evidence, and bounded menu parsers."""
from html.parser import HTMLParser
import re
from urllib.parse import urljoin, urlparse

BIG = 'https://bigbitesshawarma.com/'
PITA = 'https://pitadeliwhitby.com/'
CORK = 'https://corkandbean.ca/oshawa/menu/'
OSMOW = 'https://osmows.com/dailyspecials/'
TACO = 'https://www.tacobell.ca/en/menu'

# A branch page proves an address. Only that branch's own priced menu proves a price.
BRANCHES = [
    dict(id='bigbites-rossland',brand='Big Bites Shawarma',town='Oshawa',address='500 Rossland Road West, Unit 3, Oshawa',phone='905-432-8838',url=BIG,needle='500 Rossland',pricedMenu=True),
    dict(id='pitadeli-champlain',brand='Pita Deli',town='Whitby',address='1600 Champlain Ave, Whitby',phone='905-725-8152',url=PITA,needle='1600 Champlain',pricedMenu=True),
    dict(id='corkbean-simcoe',brand='Cork & Bean',town='Oshawa',address='8 Simcoe St N, Oshawa',phone='905-240-2326',url=CORK,needle='8 Simcoe',pricedMenu=True),
    dict(id='mc-ritson',brand='McDonald’s',town='Oshawa',address='501 Ritson Rd S, Oshawa',url='https://www.mcdonalds.com/ca/en-ca/location/oshawa/oshawa-ritson/501-ritson-rd-s/3313.html',needle='501 Ritson'),
    dict(id='wendys-king',brand='Wendy’s',town='Oshawa',address='323 King St W, Oshawa',phone='905-438-0001',url='https://locations.wendys.com/canada/on/oshawa/323-king-st-w',needle='323 King'),
    dict(id='wendys-harmony',brand='Wendy’s',town='Oshawa',address='1362 Harmony Road, Oshawa',phone='905-404-4400',url='https://locations.wendys.com/canada/on/oshawa/1362-harmony-road',needle='1362 Harmony'),
    dict(id='wendys-paisley',brand='Wendy’s',town='Whitby',address='1 Paisley Ct, Whitby',phone='905-665-1176',url='https://locations.wendys.com/canada/on/whitby/1-paisley-ct',needle='1 Paisley'),
    dict(id='osmows-garden',brand='Osmow’s',town='Whitby',address='3050 Garden St Unit 123, Whitby',phone='905-430-9075',url='https://locations.osmows.com/on/whitby/3050-garden-st-unit-123',needle='3050 Garden'),
    dict(id='osmows-baldwin',brand='Osmow’s',town='Whitby',address='5969 Baldwin Street South, Whitby',url='https://locations.osmows.com/on/whitby/5969-baldwin-street-south',needle='5969 Baldwin'),
    dict(id='barburrito-shores',brand='barBurrito',town='Whitby',address='617 Victoria St W, Whitby',phone='905-665-3333',url='https://www.barburrito.ca/location/whitby-shores/',needle='617 Victoria'),
    dict(id='barburrito-bowmanville',brand='barBurrito',town='Bowmanville',address='2360 Hwy 2, Bowmanville',phone='905-419-9616',url='https://www.barburrito.ca/location/bowmanville/',needle='2360 Hwy 2'),
    dict(id='thai-oshawacentre',brand='Thai Express',town='Oshawa',address='419 King Street West #2232, Oshawa',phone='905-433-8883',url='https://thaiexpress.ca/location/oshawa-centre-on/',needle='419 King Street'),
]

EXTRA_DESTINATIONS = [
    ('bk','Burger King','Royal Perks & Canadian offers','https://www.burgerking.ca/offers','🍔'),
    ('aw','A&W','Canadian coupons','https://web.aw.ca/en/coupons','🍔'),
    ('popeyes','Popeyes','Canadian offers','https://www.popeyeschicken.ca/offers','🍗'),
    ('taco','Taco Bell','Canadian coupon wallet','https://www.tacobell.ca/en/coupons','🌮'),
    ('osmows','Osmow’s','Daily specials & local ordering',OSMOW,'🥙'),
    ('pitapit','Pita Pit','Whitby menu & local ordering','https://pitapit.ca/restaurants/whitby/','🥙'),
    ('thai','Thai Express','Current promotions & rewards','https://thaiexpress.ca/promotions/','🍜'),
    ('booster','Booster Juice','Current promotions & Booster Rewards','https://boosterjuice.com/en-ca/blogs/current-promotions','🥤'),
    ('barburrito','barBurrito','Burrito promotions & app offers','https://www.barburrito.ca/news/','🌯'),
    ('starbucks','Starbucks','Canadian Rewards & personalized offers','https://www.starbucks.ca/rewards','☕'),
    ('mucho','MUCHO Burrito','Bowmanville menu & local ordering','https://locations.muchoburrito.com/en-ca/on/bowmanville/MB0038','🌯'),
]
DESTINATION_NOTES={
    'Thai Express':'Check current promotions and Blue Rewards terms. A new product promotion is not automatically a price discount.',
    'Booster Juice':'Check current smoothie and food promotions, then your Booster Rewards offers. Smoothies are drinks, not automatically complete meals.',
    'barBurrito':'Check current dated promotions and your app account. Old National Burrito Day or Black Friday announcements do not establish a deal today.',
    'Starbucks':'Check your Canadian Rewards account for eligible offers. Rewards can require prior purchases, membership or a qualifying reload; no free item is promised here.',
    'MUCHO Burrito':'Select the Bowmanville restaurant to compare pickup menu prices, bowls and burritos. No published discount is being claimed.',
}
EXTRA_SOURCES = [(brand+' offers',url) for _,brand,_,url,_ in EXTRA_DESTINATIONS]+[
    ('Taco Bell current menu',TACO),
    ('Big Bites Oshawa menu',BIG),('Pita Deli Whitby menu',PITA),('Cork & Bean Oshawa menu',CORK),
    ('RedFlagDeals RSS','https://www.redflagdeals.com/rss/deals/'),
    ('Bargainmoose RSS','https://www.bargainmoose.ca/feed'),
    ('SmartCanucks restaurant search','https://smartcanucks.ca/?s=restaurant'),
    ('SmartCanucks food search','https://smartcanucks.ca/?s=food'),
    ('Thai Express Blue Rewards','https://thaiexpress.ca/blue-rewards/'),
    ('Booster Juice rewards','https://boosterjuice.com/en-ca/pages/booster-rewards'),
    ('Starbucks Canada Rewards terms','https://www.starbucks.ca/terms/rewards'),
]+[(b['brand']+' '+b['address'],b['url']) for b in BRANCHES if not b.get('pricedMenu')]

def branch_records(pages, now):
    normal=lambda s:re.sub(r'[^a-z0-9]','',s.lower())
    return [dict(**{k:v for k,v in b.items() if k not in ('needle','pricedMenu')},
                 addressVerified=normal(b['needle']) in normal(pages.get(b['url'],'')),
                 checkedAt=now if normal(b['needle']) in normal(pages.get(b['url'],'')) else None,
                 hasPricedMenu=bool(b.get('pricedMenu')))
            for b in BRANCHES]

def local_deals(pages, make, now, days):
    found=[]
    # Product label must be immediately followed by its own price. Do not scan
    # ahead through other menu items looking for any convenient dollar amount.
    specs=[
        (BIG,'bigbites-rossland','Big Bites Shawarma','big-falafel',r'(?<!2 )Falafel Wrap\s+Vegan\s+\$(\d+\.\d{2})','Falafel wrap','main',1,True,'Chickpea-based wrap with vegetable toppings. Falafel is fried; sauces and portion still matter.'),
        (BIG,'bigbites-rossland','Big Bites Shawarma','big-chicken',r'(?<!Special )Chicken Wrap\s+\$(\d+\.\d{2})','Chicken wrap','main',1,False,''),
        (BIG,'bigbites-rossland','Big Bites Shawarma','big-falafel-two',r'2 Falafel Wraps\s*\+\s*2 Drinks\s+(?:Vegan\s+)?\$(\d+\.\d{2})','Two falafel wraps + two drinks','meal',2,False,''),
        (BIG,'bigbites-rossland','Big Bites Shawarma','big-chicken-two',r'2 Chicken Wraps\s*\+\s*2 Drinks\s+\$(\d+\.\d{2})','Two chicken wraps + two drinks','meal',2,False,''),
        (PITA,'pitadeli-champlain','Pita Deli','pita-veg',r'Vegetarian\s+\$(\d+\.\d{2})','Vegetarian pita','main',1,True,'Vegetable-forward pita. Choose the vegetables you like and ask for sauce on the side; extras can cost more.'),
        (PITA,'pitadeli-champlain','Pita Deli','pita-garden',r'Garden Salad - Small\s+\$(\d+\.\d{2})','Small garden salad','side',1,True,'A vegetable side to add to lunch. A small salad alone may not be a filling meal; compare dressing and additions.'),
        (PITA,'pitadeli-champlain','Pita Deli','pita-fattoush',r'Fatoush Salad - Small\s+\$(\d+\.\d{2})','Small fattoush salad','side',1,True,'A vegetable-based side. Dressing and bread toppings change the nutrition; this is not a full meal.'),
        (CORK,'corkbean-simcoe','Cork & Bean','cork-falafel',r'Falafel Wrap VG\s+(\d+\.\d{2})\s+Falafel, hummus','Falafel & hummus wrap','main',1,True,'Includes hummus, spinach, green pepper and red onion. Plant-forward; not a promise of low calories or sodium.'),
    ]
    verified={b['id'] for b in branch_records(pages,now) if b['addressVerified']}
    for url,branch,brand,id,pattern,title,category,serves,healthy,note in specs:
        if branch not in verified:continue
        match=re.search(pattern,pages.get(url,''),re.I)
        if not match:continue
        branchdata=next(b for b in BRANCHES if b['id']==branch)
        price=float(match[1])
        found.append(make(id,brand,title,'Published at '+branchdata['address']+'. '+('Two wraps and two drinks; buy the whole bundle.' if serves==2 else 'Regular menu price; a discount is not claimed.'),price,url,
            category=category,serves=serves,healthier=healthy,healthReason=note,
            verification='branch-menu',branchIds=[branch],priceType='bundle' if serves>1 else 'menu',
            icon='🥗' if category=='side' else '🥙',color='#e4ead6',
            days=days[:6] if url==PITA else days[:],
            requirements={'app':False,'registration':False,'membership':None,'code':None,'minimumPurchase':0,'limitPerUser':None,'note':'Published menu price; no coupon required. Order directly; delivery-platform pricing can differ.'},
            evidence={'url':url,'checkedAt':now,'matchedText':match[0]},
            terms='Official menu for this specific address. Price checked on the restaurant’s website, not by placing an order. Tax, extras and delivery can cost more; confirm final total with the restaurant. '+('Pita Deli lists Sunday as closed.' if url==PITA else '')))
    return found

def chain_additions(pages,make,days):
    found=[]
    text=pages.get(OSMOW,'')
    # Framer renders whole dollars and cents as repeated separate elements.
    price_match=re.search(r'\$(\d{1,2})(?:\s+\$\1){0,3}\s+(\d{2})(?:\s+\2){0,3}\s+PLUS TAX',text,re.I)
    dishes=['Chicken Shawarma Wrap Box','Beef Shawarma OzBox','Chicken Shawarma Poutine','Beef Shawarma Wrap Box','Falafel OzBox','Lamb Shawarma OzBox','Mixed Shawarma OzBox']
    if price_match:
        price=float(price_match[1]+'.'+price_match[2])
        for day,title in zip(days,dishes):
            # Bind day and dish within that day's block, including repeated animated headings.
            if re.search(re.escape(day)+r'(?:(?!'+('|'.join(days))+r').){0,150}'+re.escape(title),text,re.I):
                found.append(make('osmows-'+day.lower(),'Osmow’s',title+' special','The official Canadian daily-special menu lists this dish for '+day+'. Check the local order page for participation.',price,OSMOW,days=[day],category='meal',icon='🥙',color='#ede2d2',verification='chain',serves=1,requirements={'app':None,'registration':None,'membership':None,'code':None,'minimumPurchase':0,'limitPerUser':None,'note':'Daily special only on the stated day. No end date published; branch price and order requirements need confirmation.'}))
    text=pages.get(TACO,'')
    match=re.search(r'\$(\d+(?:\.\d{2})?)\s+Tacos on Tuesdays',text,re.I)
    if match:found.append(make('taco-tuesday','Taco Bell','Tuesday taco','A taco, not a full meal. The Canadian menu advertises Tuesday tacos; check the coupon wallet and your branch.',float(match[1]),TACO,days=['Tuesday'],category='snack',icon='🌮',verification='chain',requirements={'app':None,'registration':None,'membership':None,'code':None,'minimumPurchase':0,'limitPerUser':None,'note':'Eligible fillings and any app or ordering restrictions must be checked on the official offer.'}))
    return found

def enrich(deals):
    categories={'mc-coffee':'drink','mc-dessert':'dessert','mc-fries':'side','kfc-popcorn':'snack','kfc-bucket-one':'meal','mcvalue-lunch':'meal','mcvalue-breakfast':'meal','wendys-canadian':'meal'}
    for d in deals:
        d.setdefault('category',categories.get(d['id'],'coupon' if d['kind']=='coupon' else 'idea' if d['kind']=='lighter' else 'main'))
        d.setdefault('serves',1);d.setdefault('healthier',False);d.setdefault('branchIds',[])
        d.setdefault('verification','unpriced' if d['price'] is None else 'chain')
        d.setdefault('priceType','offer' if d['kind']=='meal' else 'destination')
        req=d.setdefault('requirements',{'app':None,'registration':None,'membership':None,'code':None,'minimumPurchase':0,'limitPerUser':None,'note':'Check the official offer for app, account, coupon and order restrictions.'})
        if d['id'] in ('mc-fries','mc-dessert'):
            req.update(app=True,registration=True,limitPerUser=1)
            req['minimumPurchase']=3 if d['id']=='mc-fries' else 0
            req['note']='App and registration required; one redemption per user. Eligible dates only.'
        if d['id']=='mc-fries':d['price']=0
        if d['id'].startswith('mcvalue') or d['id']=='mc-coffee':
            req.update(app=False,registration=False,note='No minimum purchase. In-store / drive-thru; not delivery. Breakfast meals until 11 a.m.')
        d['minimumSpend']=None if d['price'] is None else round(d['price']+req.get('minimumPurchase',0),2)
    return deals

class LinkParser(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.current=None;self.text=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':self.current=dict(attrs).get('href');self.text=[]
    def handle_data(self,text):
        if self.current:self.text.append(text)
    def handle_endtag(self,tag):
        if tag=='a' and self.current:self.links.append((self.current,' '.join(self.text)));self.current=None

def link_leads(results,now):
    """Collect merchant offer links and broader coupon-search pages as leads only."""
    found=[];seen=set()
    for result in results:
        if not result['ok'] or 'RSS' in result['name']:continue
        p=LinkParser();p.feed(result['raw'])
        merchant='SmartCanucks' not in result['name']
        for href,title in p.links:
            title=re.sub(r'\s+',' ',title).strip()
            url=urljoin(result['url'],href);host=urlparse(url).hostname
            if urlparse(url).scheme!='https' or not host or url in seen:continue
            if merchant and host!=urlparse(result['url']).hostname:continue
            if not re.search(r'deal|coupon|special|offer|shawarma|wrap|meal',title,re.I):continue
            if not merchant and not re.search(r'mcdonald|wendy|harvey|subway|kfc|pizza|tim horton|burger king|popeye|taco bell|osmow|pita|restaurant|thai express|booster juice|barburrito|starbucks|mucho burrito',title,re.I):continue
            if len(title)<12 or len(title)>180:continue
            seen.add(url);found.append(dict(title=title,url=url,snippet='Official merchant link — inspect price, eligible dates and branch.' if merchant else 'Coupon search lead — requires merchant confirmation.',foundAt=now,query=result['name'],status='official-link' if merchant else 'unverified'))
            if len(found)>=35:return found
    return found

def match_leads(leads,deals):
    """A third-party title only gets a match when product AND exact price agree.

    It links to the already checked offer; it never supplies a new price or code.
    """
    for lead in leads:
        lead.setdefault('status','unverified')
        title=lead['title'].casefold()
        for d in deals:
            if d['price'] is None or d.get('sourceUnavailable') or not d.get('checkedAt'):continue
            tokens=[w for w in re.findall(r'[a-z]{4,}',d['title'].lower()) if w not in ('with','meal','deal','special')]
            if not tokens or not all(t in title for t in tokens):continue
            if not re.search(r'\$'+re.escape(f"{d['price']:.2f}")+r'(?!\d)',title):continue
            if d['brand'].casefold().replace('’',"'") not in title.replace('’',"'"):continue
            lead.update(status='merchant-match',matchedDealId=d['id'],merchantUrl=d['url'])
            break
    return leads

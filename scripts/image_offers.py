"""Manually read merchant posters; revalidate their exact bytes automatically.

If artwork changes, stop publishing its transcribed prices until reviewed.
No OCR dependency or guessed day/price mapping is needed at runtime.
"""
import hashlib
import json
from pathlib import Path
import urllib.request

SPEC_PATH=Path(__file__).with_name('thai_specials.json')

def get_poster(url):
    req=urllib.request.Request(url,headers={'User-Agent':'DurhamDailyDealFinder/1.0','Accept-Encoding':'identity'})
    with urllib.request.urlopen(req,timeout=22) as response:
        return response.read(2_000_000)

def thai_discovery(raw_pages,make,now,read=get_poster):
    spec=json.loads(SPEC_PATH.read_text())
    source=dict(name='Thai Express daily-special poster',url=spec['posterUrl'],checkedAt=now,ok=False)
    if spec['campaign'] not in raw_pages.get(spec['promotionUrl'],'') or '/discovery-menu-week/' not in raw_pages.get(spec['listingUrl'],''):
        source['error']='Discovery campaign is not currently linked in official promotions.'
        return [],source
    try:body=read(spec['posterUrl'])
    except (OSError,ValueError) as error:
        source['error']='Poster source unavailable: '+str(error)[:120]
        return [],source
    if hashlib.sha256(body).hexdigest()!=spec['sha256']:
        source['error']='Poster changed; daily-special transcription needs review.'
        return [],source
    source['ok']=True;offers=[]
    for day,dish in spec['days'].items():
        for version,price,addition in [('Duo',spec['duoPrice'],'an imperial roll OR a 20 oz drink'),('Trio',spec['trioPrice'],'an imperial roll AND a 20 oz drink')]:
            offers.append(make('thai-'+day.lower()+'-'+version.lower(),'Thai Express',dish+' '+version,
                day+' Discovery Menu special: the featured dish with '+addition+'.',price,spec['promotionUrl'],
                days=[day],category='meal',isDailySpecial=True,verification='chain-image',priceType='offer',
                icon='🍜' if 'Pad' in dish else '🍛',color='#f4dfd9',posterUrl=spec['posterUrl'],
                evidence={'url':spec['promotionUrl'],'posterUrl':spec['posterUrl'],'matchedText':day+': '+dish+'; '+version+' $'+f'{price:.2f}'},
                redemption='Check participating branch',
                requirements={'app':None,'registration':None,'membership':None,'code':None,'minimumPurchase':0,'limitPerUser':None,'note':'Duo includes an imperial roll OR a 20 oz drink; Trio includes both. Confirm eligible protein, substitutions and local participation. No app or membership requirement is established by the poster.'},
                terms='Transcribed from the current official Canadian Discovery Menu poster and rechecked against its exact image. Chain-wide advertised price; the Oshawa branch price and final tax/extra charges are not confirmed. No end date is published; the listing is removed when the linked campaign or poster changes.'))
    return offers,source

import datetime as dt
import json
from pathlib import Path
from urllib.parse import urlparse

p=Path(__file__).resolve().parents[1]/'docs/data/deals.json'
data=json.loads(p.read_text())
dt.datetime.fromisoformat(data['generatedAt'])
ids=set()
days={'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'}
for d in data['deals']:
    assert d['id'] not in ids, f'Duplicate ID: {d["id"]}'
    ids.add(d['id'])
    assert d['kind'] in {'meal','coupon','lighter'}
    assert d['days'] and set(d['days'])<=days
    assert d['price'] is None or type(d['price']) in (int,float) and 0<d['price']<100
    assert urlparse(d['url']).scheme=='https'
    assert d['title'] and d['brand'] and d['terms']
    if d['price'] is not None:assert d['checkedAt'], 'Priced deal needs source check'
    for key in ['starts','ends']:
        if d.get(key):dt.date.fromisoformat(d[key])
    for date in d.get('dates',[]):assert dt.date.fromisoformat(date).strftime('%A') in d['days']
print(f'Validated {len(ids)} offers, coupons and healthier ideas.')

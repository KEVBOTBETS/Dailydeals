import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import image_offers as im
from scripts import refresh as r

class ThaiPosterTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=Path(self.temp.name)/'poster.json'
        self.body=b'confirmed merchant poster fixture'
        self.spec=json.loads(im.SPEC_PATH.read_text())
        self.spec['sha256']=hashlib.sha256(self.body).hexdigest()
        self.path.write_text(json.dumps(self.spec))
        self.pages={self.spec['promotionUrl']:self.spec['campaign'],self.spec['listingUrl']:'/discovery-menu-week/'}
        self.patch=patch.object(im,'SPEC_PATH',self.path);self.patch.start()
    def tearDown(self):self.patch.stop();self.temp.cleanup()
    def test_seven_correct_days_with_duo_and_trio(self):
        ds,source=im.thai_discovery(self.pages,r.deal,r.NOW,lambda _:self.body)
        self.assertTrue(source['ok']);self.assertEqual(len(ds),14)
        tuesday=[d for d in ds if d['days']==['Tuesday']]
        self.assertEqual([d['title'] for d in tuesday],['Pad See Ew Duo','Pad See Ew Trio'])
        self.assertEqual([d['price'] for d in tuesday],[13.88,14.88])
        self.assertTrue(all(d['verification']=='chain-image' for d in ds))
    def test_changed_image_does_not_reverify_old_prices(self):
        ds,source=im.thai_discovery(self.pages,r.deal,r.NOW,lambda _:b'new poster')
        self.assertEqual(ds,[]);self.assertFalse(source['ok']);self.assertIn('changed',source['error'])
    def test_archived_poster_not_promoted_when_campaign_unlinked(self):
        self.pages[self.spec['listingUrl']]='Other promotion'
        ds,source=im.thai_discovery(self.pages,r.deal,r.NOW,lambda _:self.body)
        self.assertEqual(ds,[]);self.assertFalse(source['ok'])
    def test_failed_download_does_not_refresh_prices(self):
        def fail(_):raise OSError('timeout')
        ds,source=im.thai_discovery(self.pages,r.deal,r.NOW,fail)
        self.assertEqual(ds,[]);self.assertTrue(source['error'].startswith('Poster source unavailable:'))

if __name__=='__main__':unittest.main()

# Durham Daily

A responsive, buildless fast-food deal board for **Durham Region, Ontario**, in CAD. Designed for GitHub Pages at `https://kevbotbets.github.io/Dailydeals/` once deployment succeeds.

## Features

- Monday–Sunday and all-week views, Toronto-local “today”, search, budget and restaurant sorting.
- Pickering, Ajax, Whitby, Oshawa, Courtice, Bowmanville, Newcastle, Uxbridge, Port Perry, Beaverton and Cannington nearby searches. Town selection changes map/web queries; it does **not** assert branch participation.
- Separate published offers, coupon/app destinations and healthier menu ideas. Unpriced coupons and healthier ideas are excluded by budget caps.
- Favorites saved in this browser, source dates, explicit expiry dates and stale-feed warnings.
- Automatic Python collector checks public Canadian merchant pages and scans Canadian coupon RSS feeds for restaurant leads. No API keys or paid services.
- GitHub Actions refreshes at **12:00 and 18:00 UTC** daily (7am/1pm Toronto winter, 8am/2pm summer), commits the feed and republishes Pages. GitHub can delay scheduled runs. Manual runs: Actions → Refresh deals and publish → Run workflow.

## Publishing

The workflow requests Pages enablement and publishes `docs/`. If GitHub requires one-time repository setup, go to **Settings → Pages → Source → GitHub Actions**, then rerun the workflow. Enable Actions if disabled. Workflow permission must allow `contents: write`, `pages: write` and `id-token: write`. No external credentials are stored.

## Data and honesty

`scripts/refresh.py` has small, explicit rules for current public official offers. Prices are extracted only when the matching product is present. Time-limited offers have expiry bounds. A publication/source check is **not** a checkout test or verification at a Durham branch. Account-only coupons cannot be scraped; use the official app. An unavailable source can retain a previously checked priced offer for at most three days with its original timestamp and an outage flag. A successful fetch without the offer removes it immediately. Stale prices are not treated as newly checked.

RSS results are **unverified internet leads** and never promoted into priced offers. Feed failures are visible under source checks. New arbitrary offers require a new bounded extraction rule in `official_deals`; this collector is not a general-purpose AI deal verifier. Local independent restaurant specials can be discovered through the town-specific search links but are not automatically declared valid. No invented coupon codes, calories, protein numbers, savings percentages or expiry dates. Healthier entries are qualitative customization ideas with menu/nutrition links, not promised discounted meals.

## Run and maintain

Requires Python 3.12+ and Node 22+ for checks. The frontend needs no dependencies or build step.

```sh
python scripts/refresh.py
python scripts/validate.py
python -m unittest discover -s tests -v
node --test tests/*.test.cjs
python -m http.server 8000 --directory docs
```

Open `http://localhost:8000`. Use a server rather than opening `index.html` as a file because the feed is loaded with fetch. UI: `docs/index.html`, `docs/styles.css`, `docs/app.js`; filtering: `docs/deal-logic.js`; generated feed: `docs/data/deals.json`. Add source URLs and extraction rules with tests. Do not use a page-wide dollar amount for an unrelated product. Preserve original date lists for occasional offers rather than treating them as permanent weekday specials.

External Google Fonts are optional; system font fallbacks work if blocked. No analytics, login, or precise location collection. Saved preferences stay on the visitor’s browser.

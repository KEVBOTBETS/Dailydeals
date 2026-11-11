# Durham Daily

A responsive, buildless fast-food deal board for **Durham Region, Ontario**, in CAD. Designed for GitHub Pages at `https://kevbotbets.github.io/Dailydeals/` once deployment succeeds.

## Features

### Local price and discovery upgrade

- The first view shows **full meals and combos**; mains, wraps, snacks, sides, desserts, drinks, coupon destinations and healthier choices have separate filters.
- Town and exact-branch filters use official branch records. **Branch prices checked only** requires a fresh priced menu at that address, matching product evidence, and a fresh address check. A chain branch directory entry cannot verify a chain price.
- Current local parsers cover Big Bites Shawarma (500 Rossland Road West, Oshawa), Pita Deli (1600 Champlain Ave, Whitby) and Cork & Bean (8 Simcoe St N, Oshawa). These are published menu quotes, not completed checkouts. Pita Deli is excluded on Sunday.
- Priced healthier choices include vegetarian pitas and falafel wraps, with an explanation of ingredients and tradeoffs. Small vegetable salads remain **sides**, not full meals. No calorie or low-sodium claims are invented.
- Every priced card shows the **whole minimum required spend** before tax. Conditional freebies include the required purchase; two-person bundles retain their whole basket total for sorting and budget caps. Per-person prices are secondary. App, registration and redemption restrictions are visible.
- The three best-value slots use only fresh branch-menu quotes within the selected area and filters: cheapest complete meal/combo, lowest-priced plant-forward main, and lowest whole spend for two. A two-person bundle is labelled as such, including on the cheapest-combo slot. Singles can be doubled only when no single-use restriction or conditional purchase prevents it. Empty categories stay empty. This is a comparison among the collected offers, not every restaurant in Durham.
- Coverage includes Burger King, A&W, Popeyes, Taco Bell, Osmow’s, Pita Pit, **Thai Express, Booster Juice, barBurrito, Starbucks**, MUCHO Burrito and independent Durham restaurants, alongside the original chains. Unpriced destinations do not claim a live discount. Selecting a restaurant shows all its offer types, so a coffee/rewards destination is not hidden by the default meal filter.
- Discovery checks additional Canadian coupon feeds, restaurant search pages, merchant offer links, local menus and branch pages. Leads stay unverified unless the title’s brand, product and exact advertised price match an independently extracted merchant offer. Such a match links to merchant evidence and does not prove branch participation or add a new code.

### Original capabilities

- Monday–Sunday upcoming-date and next-seven-day views, Toronto-local “today”, search, budget and restaurant sorting.
- Pickering, Ajax, Whitby, Oshawa, Courtice, Bowmanville, Newcastle, Uxbridge, Port Perry, Beaverton and Cannington nearby searches. Town selection changes map/web queries; it does **not** assert branch participation.
- Separate published offers, coupon/app destinations and healthier menu ideas. Unpriced coupons and healthier ideas are excluded by budget caps.
- Favorites saved in this browser, source dates, explicit expiry dates and stale-feed warnings.
- Automatic Python collector checks public Canadian merchant pages and scans Canadian coupon RSS feeds for restaurant leads. No API keys or paid services.
- GitHub Actions refreshes at **12:00 and 18:00 UTC** daily (7am/1pm Toronto winter, 8am/2pm summer), commits the feed and republishes Pages. GitHub can delay scheduled runs. Manual runs: Actions → Refresh deals and publish → Run workflow.

## Publishing

The workflow requests Pages enablement and publishes `docs/`. If GitHub requires one-time repository setup, go to **Settings → Pages → Source → GitHub Actions**, then rerun the workflow. Enable Actions if disabled. Workflow permission must allow `contents: write`, `pages: write` and `id-token: write`. No external credentials are stored.

## Data and honesty

`scripts/refresh.py` has small, explicit rules for current public official offers. Prices are extracted only when the matching product is present. Time-limited offers have expiry bounds. A publication/source check is **not** a checkout test or verification at a Durham branch. Account-only coupons cannot be scraped; use the official app. An unavailable source can retain a previously checked priced offer for at most three days with its original timestamp and an outage flag. A successful fetch without the offer removes it immediately. Stale prices are not treated as newly checked.

RSS results are **unverified internet leads** and never promoted into priced offers. Feed failures are visible under source checks. New arbitrary offers require a bounded extraction rule in `official_deals`, `catalog.local_deals` or `catalog.chain_additions`; this collector is not a general-purpose AI deal verifier. Local independent restaurant specials can be discovered through the town-specific search links but are not automatically declared valid. No invented coupon codes, calories, protein numbers, savings percentages or expiry dates. Healthier entries include priced local menu items and separate unpriced customization ideas. A regular menu price is never presented as a sale.

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

## Food preference and Thai Express daily specials

Shawarma restaurants and dishes are hidden by default from cards, restaurant and branch selectors, branch listings and best-value picks. The Hide shawarma restaurants preference is saved in this browser and survives Reset filters. Uncheck it to include those offers. This does not exclude unrelated vegetarian wraps or all Middle Eastern food.

Thai Express Discovery Menu Duos ($13.88) and Trios ($14.88) are listed for all seven days, using the current official 2026 poster. Duo includes an imperial roll OR a 20 oz drink; Trio includes both. The default Any price budget includes offers above $10. The Daily specials filter makes the lineup easy to find. A deliberately selected budget cap still applies. These are advertised Canadian chain prices, not branch-confirmed prices.

`scripts/thai_specials.json` records the manually inspected weekly image, exact SHA-256, dishes and prices. `image_offers.py` checks that official current promotions still link the Discovery Menu, its page still references the same campaign, and the official poster bytes still match. A changed/unlinked campaign removes the transcription until reviewed. A temporary image-download failure can keep an old quote for up to three days with its original timestamp and an unavailable-source label; it cannot reverify the quote. No OCR or image library is needed on GitHub Actions.

When no branch-checked complete combo matches, the first highlight can feature the current Thai Express special instead; it is labelled as an advertised chain special requiring branch confirmation. Healthier and two-person comparisons still require branch menu evidence.

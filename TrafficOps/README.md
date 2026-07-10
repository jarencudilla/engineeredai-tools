# TrafficOps — MVP Slice

Single site at a time, GSC + GA4, pull → normalize → store → display.
No multi-select, no AI yet. See `docs/TrafficOps-v1-Spec.md` for the full spec.

## 1. Setup (one-time)

```bash
cd TrafficOps
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Service account key (one-time)

You already have the TrafficOps Cloud project, the Search Console API and
GA4 Data API enabled, and `trafficops-reader@trafficops.iam.gserviceaccount.com`
added as Viewer on each site in both Search Console and GA4. One step left:

1. Cloud Console → **IAM & Admin → Service Accounts** → click `trafficops-reader`
2. **Keys** tab → **Add Key → Create new key → JSON**
3. Save the downloaded file as `config/credentials.json` (this exact path — it's gitignored, never commit it)

One key authenticates against both APIs, for all six sites — access is
controlled per-site inside each product's own console, not by separate
credential files.

## 3. Get GA4 property IDs (one script, not six manual lookups)

```bash
python -m scripts.discover_ga4_properties
```

This lists every GA4 property your service account can see, with the
numeric `ga4_property_id` next to each. Match each one to a site by
name and paste it into `config/sites.py`, replacing that site's
`"ga4_property_id": None`.

This only needs to run once — it's a lookup, not a repeated setup step.

## 4. Run it

```bash
python -m app.main
```

## 5. What this MVP slice proves

- Service account auth works end-to-end for both GSC and GA4, one key for all six sites
- Data pulls, normalizes (shared URL canonicalization across both sources), and stores per-site
- Tables render from the database, not live from the API (Sync and View are separate steps)
- Re-running Sync updates existing rows instead of duplicating them
- GSC and GA4 sync independently — one failing doesn't block the other

## 6. Known gaps (intentional — not bugs)

- **Single-thread sync.** Both syncs run on the UI thread. Fine for one site / short date ranges. Move to a worker thread before combining sites or pulling long ranges (see spec's Performance section).
- **No GSC pagination.** Responses over 25,000 rows will silently truncate. Not a concern at current traffic levels, but flagged for when it becomes one.
- **7-day pull window, hardcoded** for both sources.
- **GSC and GA4 aren't joined yet.** Both are stored per-site with canonicalized URLs so a join ("impressions but no clicks" vs "clicks but no engagement") is possible later — that join itself is Phase 3 (Deterministic analysis), not built here.
- **One site wired into the UI dropdown at a time.** All six are registered in `config/sites.py`, but multi-select (open several `.db` files and merge in memory) isn't built yet.

## 6. Folder reference

| Folder | Responsibility |
|---|---|
| `app/` | Entry point + orchestration (sync pipeline wiring) |
| `ui/` | Qt widgets — rendering only, no business logic |
| `collectors/` | Talks to GSC API + OAuth. Returns raw data, no shaping. |
| `services/` | Normalization — raw API data → GSCQueryRow |
| `database/` | The only module that touches sqlite3 directly |
| `models/` | Data shapes shared across layers |
| `config/` | Site registry, credentials, cached tokens (gitignored) |

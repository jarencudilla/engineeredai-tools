# TrafficOps — MVP Slice

Single site (QAJourney), GSC only, pull → normalize → store → display.
No GA4, no multi-select, no AI yet. See `docs/TrafficOps-v1-Spec.md` for the full spec.

## 1. Setup (one-time)

```bash
cd TrafficOps
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Google Cloud OAuth setup (one-time)

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → create a project (or reuse one).
2. Enable the **Search Console API**.
3. Go to **APIs & Services → Credentials → Create Credentials → OAuth client ID**.
   - Application type: **Desktop app**
4. Download the JSON, save it as `config/credentials.json` (this exact path — it's gitignored, never commit it).
5. Make sure the Google account you'll authenticate with has **at least Viewer access** in Search Console for each site you sync — you mentioned this is already done.

## 3. Run it

```bash
python -m app.main
```

First time you hit **Sync** on a given site, a browser window opens for Google consent.
After that, the token is cached in `config/tokens/{site}_token.json` and reused silently.

## 4. What this MVP slice proves

- OAuth flow works end-to-end for one site
- GSC data pulls, normalizes (URL canonicalization), and stores in `data/qaj.db`
- Table renders from the database, not live from the API (Sync and View are separate steps)
- Re-running Sync updates existing rows instead of duplicating them

## 5. Known gaps (intentional — not bugs)

- **Single-thread sync.** Sync runs on the UI thread. Fine for one site / short date ranges. Move to a worker thread before combining sites or pulling long ranges (see spec's Performance section).
- **No pagination.** GSC responses over 25,000 rows will silently truncate. Not a concern at current traffic levels, but flagged for when it becomes one.
- **7-day pull window, hardcoded.** `app/sync.py` defaults to `days_back=7`. Date range picker is Phase 2.
- **One site wired into the UI dropdown at a time.** All six are registered in `config/sites.py`, but multi-select (per our earlier discussion — open several `.db` files and merge in memory) isn't built yet. Adding it later doesn't require touching this slice's code, just a new selection mode in `main_window.py`.

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

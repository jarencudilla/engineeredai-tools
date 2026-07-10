# TrafficOps v1 Specification

## Project Goal

TrafficOps is a local-first desktop analytics application built for content publishers who need operator-level visibility into their websites.

It is not an SEO SaaS.

It is not an Ahrefs clone.

It is not another dashboard full of pretty graphs.

Its purpose is to answer questions that Site Kit and GA4 do not answer efficiently.

Examples:

- Why is this page getting impressions but no clicks?
- Why is this page getting clicks but no engagement?
- Which pages are silently performing well?
- Which posts are decaying?
- Which queries deserve follow-up articles?
- Which pages are trusted by AI crawlers?
- Which content clusters are working?

## Design Philosophy

TrafficOps is designed like an operator tool.

Think:

- Screaming Frog
- DB Browser for SQLite
- Wireshark
- Process Explorer

Data first.

Charts second.

Tables over dashboards.

Investigation over presentation.

## Tech Stack

**Language:** Python

**IDE:** VS Code

**GUI:** PySide6 (Qt)

**Database:** SQLite

**Exports:** CSV, JSON, Markdown

**AI:** Optional local Ollama integration. No cloud AI required.

## Architecture

```
TrafficOps/
├── app/
├── ui/
├── collectors/
├── analyzers/
├── services/
├── database/
├── models/
├── cache/
├── exports/
├── config/
├── docs/
└── logs/
```

Everything has a single responsibility.

## Core Principles

**Local First** — Everything runs locally. No hosted backend. No cloud database.

**Deterministic First** — Business logic never depends on AI. Calculations are performed by code. AI only provides optional interpretation.

**Progressive Loading** — Never wait for the whole pipeline. Each completed stage updates immediately.

Example:
```
✓ GA4
✓ GSC
⟳ Competitor Scan
✓ Landing Pages
⟳ AI Analysis
```

**Fault Tolerant** — Every module assumes failures. Required: timeouts, retries, fallbacks, caching.

## Data Storage & Site Selection

**Storage model: one SQLite file per site.**

Each site in the network gets its own isolated database (e.g. `qaj.db`, `eai.db`, `mmp.db`, `hf.db`, `rwh.db`, `he.db`). This is the storage layer and does not change based on how the UI is used.

Rationale:
- No `site_id` filtering on every query — each file is already scoped
- No risk of a query bug leaking one site's rows into another's results
- Matches the DB Browser for SQLite workflow — any single site's file can be opened and inspected in isolation, with no other site's data as noise
- Backup, reset, or rebuild of one site's data is a single-file operation and doesn't touch the other five

**UI selection is independent of storage and supports both modes:**

- **Single-select** — dropdown picks one site → only that site's `.db` file is opened → tables and Inspector render from that file alone.
- **Multi-select** — user selects any combination of sites, up to all six → the app opens each selected site's `.db` file and combines results in memory (Python) before rendering.

Multi-select does not require a schema change or a shared database. It's an aggregation step at the application layer, not a storage-layer decision — the same pattern used by tools like Screaming Frog, which keep per-crawl files separate and combine them only at the point of analysis.

**Known tradeoff:** true cross-site SQL joins (e.g. one query across all six sites' raw tables) aren't possible with this model — multi-site views are always a merge-after-read. This is acceptable for V1 and does not block later work; a network-wide aggregation layer can be added on top without touching the per-site storage format.

**Credentials:** Since this is local-only, GA4/GSC OAuth tokens or service account keys should be stored per-site in a local encrypted file (or OS keychain, if available), not in plaintext config and not synced anywhere. This lives alongside — but separate from — each site's `.db` file.

## Initial Data Sources

**Google Analytics 4** (primary source)

Examples: sessions, engagement, landing pages, traffic source, country, events

**Google Search Console** (primary source)

Examples: queries, impressions, CTR, average position, pages

**Future:** Server logs, Cloudflare, Bing Webmaster, Manual CSV import

## MVP

The MVP is intentionally small.

Requirements:

1. Connect to GA4 (per site).
2. Connect to GSC (per site).
3. Pull data.
4. Normalize data.
5. Store in per-site SQLite file.
6. Display in UI, scoped to selected site(s).
7. Export CSV.

If this works, the MVP is complete.

## Phase 2

Add: Filtering, Sorting, Searching, Date ranges, Saved filters, Bookmarks

## Phase 3

Deterministic analysis. Examples: High impressions/low CTR, High CTR/low engagement, Decaying pages, Silent winners, False winners. No AI yet.

## Phase 4

Competitor Intelligence. Public information only. No paid APIs.

Examples: Ranking pages, SERP titles, Keyword overlap, Content gaps

*Note: SERP scraping is subject to detection/blocking by Google and may need reassessment when this phase is reached.*

## Phase 5

Optional AI Layer. AI is NOT required.

UI contains "Enable AI Analysis" — when disabled, everything still works. When enabled, current table or selected rows are sent to Ollama.

Examples: Analyze page, Analyze competitor, Explain decay, Suggest follow-up topics, Suggest title improvements

## UI Layout

**Toolbar:** Sync, Export, Settings

**Sidebar:** Dashboard, Sites (site selector — single or multi), Pages, Queries, Landing Pages, Competitors, AI, Reports, Settings

**Main Area:** Tables, Inspector Panel, Status Bar

## Dashboard

Overview only. Cards: Sessions, Impressions, Clicks, CTR, Average Position, Engagement

No fancy charts required.

## Pages Module

Columns: URL, Sessions, Engagement, Bounce, Entrances, Exits, Events

Clicking a page updates the Inspector.

## Queries Module

Columns: Query, Clicks, Impressions, CTR, Position

Allows: Sort, Filter, Export

## Landing Pages Module

Columns: Landing Page, Sessions, Bounce, Avg Engagement, Events

## Inspector Panel

Shows details for selected row.

Example: Page → Queries → Traffic → Engagement → History → AI Analysis (optional)

## AI Panel

Optional. Never automatic. Button driven.

Example: "Analyze Selected Page" — prompt receives structured JSON. Never raw database dumps.

## Performance

Long tasks use worker threads. UI never freezes. Maximum concurrent sync jobs configurable.

## Timeouts

Each stage has independent timeout.

Example: GA4 — 20s, GSC — 20s, Competitor — 45s, AI — 60s

## Fallbacks

If API fails → Use cached data

If AI fails → Return deterministic analysis only

If cache unavailable → Show error

Never crash.

## Export Formats

CSV, JSON, Markdown

Future: Excel, PDF

## Coding Standards

- Every file begins with a module docstring.
- Every public function has a docstring.
- Comments explain why, not what.
- Business logic never belongs in UI classes.
- UI only renders.
- Collectors only collect.
- Analyzers only analyze.
- Database only stores.
- No module should do multiple jobs.

## Documentation

Each major folder contains a README explaining: Purpose, Responsibilities, Inputs, Outputs, Dependencies

Future maintenance should not require reverse engineering.

## Long-Term Vision (Not V1)

AI crawler detection, Server log ingestion, Cloudflare analytics, Internal link visualization, Content cluster mapping, Decay prediction, Monetization attribution, Historical comparisons, Multi-machine sync, Plugin architecture

These are intentionally out of scope for the MVP.

## Final Guiding Rule

If the feature doesn't help answer a publishing or traffic question using deterministic data, it does not belong in V1.

That rule should keep the project focused and prevent scope creep while leaving a clean path for future expansion.

# AutoBlog AI — Changelog

---

## v3.4 (2026-03-09) — Dashboard as Sole Source of Truth

- Removed ALL runtime defaults from load_config — config.json is never overwritten at runtime
- Removed decommissioned model auto-replace from load_config (was silently overwriting dashboard changes on every API call)
- Added migrate_config() — runs ONCE at startup only, fixes known bad model strings, writes permanently to config.json, never runs again
- Dashboard pipeline selector now fully respected — what you set is what runs, no exceptions

---

## v3.3 (2026-03-09) — Content Quality Fixes

- Stage 2 Writer: Banned filler transition phrases ("we will provide", "furthermore", "in addition to our review", "moreover", "we will explore", etc.)
- Stage 2 Writer: Explicit rule against ending sections with meta-commentary about future sections
- Stage 2 Writer: Write like a person not a content robot — specific, direct, useful
- Stage 2 default reverted to Groq / llama-3.3-70b-versatile (Mistral 7B local not following prompt rules reliably)

---

## v3.2 (2026-03-09) — Prompt & Output Quality Fixes

- Stage 2 Writer: Enforce body-only HTML output — no DOCTYPE, no html/head/body tags, start with first h2
- Stage 2 Writer: Strict internal linking — only use URLs from sitemap list, never hallucinate URLs
- Stage 2 Writer: Each URL max once per article, only link when genuinely relevant
- Stage 2 Writer: No concept repetition for word padding — each paragraph must introduce new information
- Stage 2 Writer: Amazon affiliate links placed inline within content, descriptive anchor text, no Resources section dump at bottom
- Stage 3 Editor: Safety strip — detects and removes full HTML boilerplate if Stage 2 returns a full document
- Stage 4 Curator: Safety strip — same boilerplate detection and removal as Stage 3
- Stage 5 Metadata: Removed old Amazon link appending block — links now handled inline by Stage 2

---

## v3.1 (2026-03-09) — Pipeline Stability Fixes

- Fixed default model strings — was gemini-2.5-pro-preview-06-05 (does not exist), corrected to gemini-2.0-flash
- Added proper error logging — prints full Groq/Gemini response body before raising, so errors are diagnosable
- Added rate limit retry handler — waits 65s and retries once on 429
- Added 3s delay between pipeline stages to prevent rate limit bursts
- Removed all hardcoded model/provider values from pipeline logic
- All model routing goes through call_model() and dashboard config only
- Fixed existing_topics join error (str coercion on set items)
- Removed draft_html hard truncation (was masking real error, not fixing it)
- load_config: dashboard is now source of truth — existing pipeline values in config.json are never overridden by DEFAULT_CONFIG on startup
- load_config: auto-replaces decommissioned models on startup (mixtral-8x7b-32768 → llama-3.3-70b-versatile)
- Root cause of original Stage 3 Groq 400 identified: mixtral-8x7b-32768 was decommissioned by Groq, not a context size issue as originally suspected

---

## v3.0 (2026-03-05) — Initial Release

- 6-stage pipeline: Strategist → Writer → Editor → Curator → Metadata → Proofread
- Multi-provider support: Groq, Gemini, Mistral, OpenRouter, Anthropic, Ollama
- Dashboard-driven pipeline config — provider and model per stage, no hardcoding
- Review queue with inline editor — approve or reject before publishing
- WordPress REST API publisher — posts directly to WP with slug, excerpt, categories, tags
- Amazon affiliate link injection for monetization article type
- Sitemap-based internal linking — fetches live sitemap and passes URLs to writer
- Scheduler with per-niche interval control — auto-publishes on a cadence
- Article type mix per niche — 6 types: Informational, Shock, Editorial, Viral, Monetization, News
- Per-niche author persona (Alfred for HealthyForge/HobbyEngineered, Edwin for MomentumPath/RemoteWorkHaven)
- Four sites configured: HealthyForge, MomentumPath, RemoteWorkHaven, HobbyEngineered
- Experiment parameters: 4 sites × 1 post/day × 14 days = 56 posts

---

## v2.0 (2026-03-04) — Architecture Rebuild

- Rebuilt from v1 prototype as a proper Flask app with REST API backend
- Separated dashboard (index.html) from pipeline logic (app.py)
- Added config.json as persistent store for all settings — no hardcoded values
- Added multi-site support — unlimited WordPress sites
- Added per-niche configuration — keywords, tone, article mix, author
- Added review queue (review_queue.json) separate from published log (posts_log.json)

---

## v1.0 (2026-03-01) — Prototype

- Single-site proof of concept
- Hardcoded Gemini API for all stages
- Basic 3-stage pipeline: Topic → Draft → Publish
- No review queue — published directly to WordPress
- No dashboard — config via Python constants
- Demonstrated end-to-end WordPress publishing via REST API
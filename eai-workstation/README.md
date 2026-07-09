# EAI Workstation

A local-first AI chatbot that runs on Ollama — the free, no-subscription replacement for Claude/ChatGPT when funds or session limits get in the way. Built for one person's real workflow: content writing across the CAS network, EchoCast/ReelCast syndication, QA retainer work, coding, and brainstorming.

This is the successor to **Alfred** — same skill files, same job, but a chat UI instead of Discord and a Python backend instead of n8n. Nothing from the Discord/n8n system carries forward as infrastructure; the skill.md + companion pattern carries forward as content.

An **EngineeredAI.net (EAI)** project.

---

## What This Is

- Local LLM chat via Ollama — no cloud, no subscription, no session timeouts
- Global chat as the home screen, always available — no mode to pick before you can talk
- Optional workspace/folder tagging, manual only — never auto-sorted
- Skills fire based on what you say (site names, URLs, phrasing), same principle as Claude skill descriptions, just implemented as deterministic matching
- Full-text recall (SQLite FTS5) across all chat history by default
- On-demand web access for fact-checking and sourcing, callable from any chat
- Packaged as a single double-click executable — no terminal, ever

## What This Is Not

Not frontier-quality — a 6GB-VRAM local model won't match Claude or GPT output. It needs to be good enough to edit, not rewrite from scratch. Not an agent framework, not multi-user, not a SaaS. This is a workstation for one person.

---

## Stack

| Layer | Choice |
|---|---|
| Backend | Python + FastAPI |
| Desktop UI | pywebview (HTML/CSS/JS) |
| LLM runtime | Ollama (external process, not bundled) |
| Storage | SQLite + FTS5 (full-text search, no vector DB for V1) |
| Skill routing | Plain Python pattern/keyword matching — deterministic, not AI-guessed |
| Packaging | PyInstaller (`--onefile`, `--windowed`) |
| Target OS | Windows |

## Target Hardware

GTX 1660 (6GB VRAM). Target quant: Q4. Target models: Gemma 3, Qwen 2.5, Mistral, or other free Ollama-compatible models. Workspace-level model swapping assumed rather than one model serving everything.

---

## Repo Structure

```
app/
├── backend/
│   ├── main.py              # FastAPI entrypoint
│   ├── config.py             # Paths, port, target model
│   ├── logging_setup.py      # Logging config
│   ├── db/                   # SQLite connection + schema
│   ├── ollama/                # Ollama client + health check
│   └── routers/               # API endpoints
├── skills/                    # Ported skill.md + companion files (Phase 5)
└── data/                      # SQLite database file (gitignored)
```

Backend is built and tested **headless first** — via FastAPI's `/docs` — before any UI code is written. The UI is a skin; it contains no business logic.

Every file targets ~200 lines max, single responsibility, per CAS coding standards.

---

## Build Order

1. **Foundation** — FastAPI skeleton, SQLite, Ollama health check (headless)
2. **Chat** — send/receive, streaming, save to SQLite (headless)
3. **Recall** — FTS5 search across all chat history (headless)
4. **UI Skin** — pywebview window on top of the working backend
5. **Skill Router + Runtime Loader** — content-based skill matching, ported from the Alfred skill.md/companion pattern
6. **Workspace Tagging** — manual folder/project organization
7. **Web Access** — on-demand fetch/search from any chat
8. **Ollama Onboarding** — detect-and-guide install/model-pull flow, no terminal
9. **Packaging** — PyInstaller build, tested end-to-end on a clean machine

Mobile companion, semantic search, and additional model providers are explicitly deferred past V1.

---

## Status

🚧 Phase 1 — Foundation. Not yet functional.

---

## Non-Goals

No agents, no multi-agent framework, no SaaS, no cloud sync, no multi-user, no AI OS.

## Engineering Filter

Before adding anything not already scoped:

> Does this help continue writing, coding, QA, and research when Claude/ChatGPT aren't available?

Yes → belongs in V1. No → it waits.

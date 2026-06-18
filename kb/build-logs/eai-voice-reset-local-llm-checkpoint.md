# EAI Voice Reset + Local-LLM Pivot — Checkpoint

**Date:** 2026-06-18
**Status:** Intentional reset, early recovery signal, direction confirmed

## Context

EAI carried a backlog of outdated, beginner-targeted, "index me Google" filler content that conflicted with the AI-enthusiast voice the site is meant to have. This content was deleted, rewritten, or redirected; hubs were created around a sharper, more focused voice and path. This was a deliberate reset, not decay — the resulting dip in traffic metrics is the expected cost of the cut, not a signal of failure.

EAI is also the only CAS site delisted from Bing (no path to resolution — closed chapter). All current EAI traffic is Google-only.

## Evidence (28-day Site Kit summary, as of 2026-06-18)

- Unique visitors: 591 (-7.9%)
- Impressions: 8.0K (-51.9%)
- Clicks: 29 (-25.6%)
- Avg time on page: 57s (-57.4%)

These are blended 28-day averages and understate a more recent recovery (see below).

## Recovery signal

- Impressions dipped to ~500/day for about a week post-reset, now climbing back to 700+/day within a 24-hour window.
- Dwell time dipped during the same window, recovered to ~1m30s a few days ago, settling back toward ~52s most recently.
- 52s dwell time pre-reset was occurring against ~2K impressions of largely low-quality/junk traffic ("spam heaven" — high impressions, low engagement). Post-reset, similar dwell time is occurring against a smaller, higher-intent traffic base. The number looks flat but the composition underneath it is healthier.
- Top performers post-reset: `llm-quantization-explained` (10 clicks, 2,055 impressions, position 8.9) and `best-local-ai-models-for-your-gpu` (7 clicks, 1,925 impressions, position 14.1) — both local-LLM content, both well ahead of everything else on the site.

## Direction

EAI's content is pivoting toward local-LLM / hardware-constrained AI as the core lane, directly downstream of building Alfred (Jaren's own Ollama-based local AI stack — Qwen 2.5 3B primary, Mistral 7B secondary, GTX 1660 6GB, sequential by hardware constraint). This is practitioner-first by construction: the content reflects problems actually hit while building Alfred, not topics selected for search volume.

Stated thesis (already published on EAI, `eai-application-breakthrough` context): local context engineering raises the floor on what a small/local model produces, not the ceiling past the model's underlying capability. The goal is not parity with frontier models — it's usable output within real hardware constraints, with an architecture (the context/prompt layer) that transfers directly if the inference endpoint is later swapped from Ollama to an API model.

Concrete example of the hardware-ceiling problem already encountered: a 9.1GB model (phi4) spilling to CPU memory and timing out on a 6GB VRAM system — a context-design failure, not a model-quality failure.

## Caveats

- EAI is the broadest, most competitive, most saturated site in the network — hardest to build by Jaren's own assessment.
- Recovery is real but early (days, not weeks) — 28-day blended metrics will lag behind the actual daily trend for a while yet.
- No Bing channel to offset or cross-check against — recovery is 100% Google-dependent.
- A queued content gap (local-LLM context window degradation on small models) is identified as a high-confidence next piece, consistent with this direction, but not yet drafted.

## Conclusion

Reset was intentional and is behaving as expected: short-term metric dip, early signs of recovery in the highest-intent content, and a content direction anchored to a real build (Alfred) rather than a strategy guess. Revisit once daily metrics have a few more weeks to stabilize.

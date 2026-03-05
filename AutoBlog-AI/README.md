AutoBlog AI — Autonomous Multi-Model Writing Engine
Status: WIP · Experiment 001 on EngineeredAI.net
An autonomous AI writing engine that runs a full editorial team across multiple WordPress blogs. Configure it once. It finds its own topics, writes full articles through a 6-stage multi-model pipeline, and publishes them on a schedule — zero input per post.

What It Does

Finds its own topics — never repeats a topic per niche, checks existing posts before generating
6-stage pipeline — Strategist → Writer → Editor → Curator → Metadata → Proofread
Multi-model — Groq, Gemini, Mistral, OpenRouter, Ollama, and Claude (optional paid)
Multi-site — unlimited WordPress sites, each with its own AI author and niches
6 article types — Informational, Viral, Monetization, Editorial, Shock, News-Style
Review queue — drafts land here first, inline editor, approve or reject before publishing
Amazon affiliate — auto-inserts links on monetization articles using your Associate tag
Fully free to run on the default Groq + Gemini stack


The Pipeline
[Niche + Schedule]
      ↓
Stage 1 — Strategist   → finds topic, search intent, outline, secondary keywords
      ↓
Stage 2 — Writer       → full draft (1200+ words, 5+ sentence paragraphs, internal links)
      ↓
Stage 3 — Editor       → challenges weak sections, cuts fluff, enforces angle
      ↓
Stage 4 — Curator      → quality gate: writing rules enforced before metadata fires
      ↓
Stage 5 — Metadata     → SEO title, slug, meta description, 10-15 keywords, excerpt
      ↓
Stage 6 — Proofread    → final grammar and flow pass
      ↓
Review Queue → Approve → WordPress REST API → Published

Free Model Stack (Default)
StageProviderModelStrategistGroqllama-3.3-70b-versatileWriterGeminigemini-2.5-proEditorGroqmixtral-8x7b-32768CuratorGeminigemini-2.0-flashMetadataGeminigemini-2.5-proProofreadGroqllama-3.3-70b-versatile
Every stage has a model selector in the dashboard. Swap to Mistral, OpenRouter, Ollama, or Claude at any time — no code changes.

Quick Start
Requirements: Windows, Python 3.12+
1. Install Python 3.12 from python.org
   → Check "Add Python to PATH" during install

2. Drop all files in one folder

3. Double-click start.bat
   → Installs dependencies automatically
   → Opens dashboard at http://localhost:5000

4. Get free API keys:
   → Groq:   console.groq.com
   → Gemini: aistudio.google.com

5. Add your WordPress sites + niches in the dashboard

6. Hit Run Now to test, then enable Auto-Publish
Full setup guide: SETUP.md

Files
FilePurposeapp.pyBackend, pipeline orchestrator, scheduler, WordPress publisherindex.htmlDashboard UIstart.batWindows one-click launcherrequirements.txtPython dependenciesSETUP.mdFull installation and configuration guide
Do not commit: config.json, posts_log.json, review_queue.json — these contain your API keys and WordPress credentials.

The Experiment
Running across 4 sites for 2 weeks: momentumpath.net, remoteworkhaven.net, healthyforge.com, hobbyengineered.com. 1 post/day per site. Full results published at the end — article quality, indexing data, affiliate clicks, cost per article.
Follow the experiment: engineeredai.net/autoblog-ai-experiment-001

Interested?
Open to licensing or acquisition conversations. Contact via EngineeredAI.net.
Pull requests welcome. If you break it, document it.

MIT License · Built by Jaren Cudilla · EngineeredAI.net
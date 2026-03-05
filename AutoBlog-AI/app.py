import os
import json
import time
import threading
import requests
import base64
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

CONFIG_FILE = "config.json"
LOG_FILE = "posts_log.json"
QUEUE_FILE = "review_queue.json"

DEFAULT_CONFIG = {
    "api_keys": {
        "gemini": "",
        "groq": "",
        "mistral": "",
        "openrouter": "",
        "anthropic": "",
        "ollama_url": "http://localhost:11434"
    },
    "pipeline": {
        "stage1_strategist": {"provider": "groq", "model": "llama-3.3-70b-versatile"},
        "stage2_writer":     {"provider": "gemini", "model": "gemini-2.5-pro-preview-06-05"},
        "stage3_editor":     {"provider": "groq", "model": "mixtral-8x7b-32768"},
        "stage4_curator":    {"provider": "gemini", "model": "gemini-2.5-pro-preview-06-05"},
        "stage5_metadata":   {"provider": "gemini", "model": "gemini-2.5-pro-preview-06-05"},
        "stage6_proofread":  {"provider": "groq", "model": "llama-3.3-70b-versatile"}
    },
    "sites": [],
    "niches": [],
    "auto_publish": False,
    "require_review": True
}

ARTICLE_TYPES = {
    "informational": {
        "name": "Informational",
        "description": "Educate readers. Clear, structured, authoritative.",
        "tone": "Neutral, expert, trustworthy. Structure: Problem → Explanation → Solution → Summary.",
        "seo_focus": "how to, what is, guide to, beginners guide"
    },
    "shock": {
        "name": "Shock/Controversy",
        "description": "Stop the scroll. Bold claims, provocative angle.",
        "tone": "Provocative, confident. Structure: Bold claim → Evidence → Counter → Double down.",
        "seo_focus": "why X is wrong, truth about, nobody tells you, stop doing"
    },
    "editorial": {
        "name": "Editorial",
        "description": "Influence opinion. Strong POV, first person voice.",
        "tone": "Opinionated, unapologetic, first person. Structure: Strong opinion → Arguments → Call to action.",
        "seo_focus": "why I think, my take on, opinion, personal experience"
    },
    "viral": {
        "name": "Viral",
        "description": "Maximum shares. Listicles, emotional hooks, relatable.",
        "tone": "Conversational, punchy, relatable. Structure: Hook → List or story → Emotional payoff → Share trigger.",
        "seo_focus": "best X, X things you didn't know, numbers in titles, you need to"
    },
    "monetization": {
        "name": "Monetization",
        "description": "Convert readers. Review, comparison, affiliate angle.",
        "tone": "Helpful, honest-feeling, subtly persuasive. Structure: Problem → Options → Recommendation → CTA.",
        "seo_focus": "best X for Y, X review, X vs Y, buyer intent, where to buy"
    },
    "news": {
        "name": "News-Style",
        "description": "Timely relevance. Journalistic, inverted pyramid.",
        "tone": "Journalistic, objective, urgent. Structure: Most important first → Context → Background.",
        "seo_focus": "trending, latest, breaking, 2025, new release"
    }
}

# ─── Config & Log helpers ────────────────────────────────────────────────────

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
        # Merge missing keys from defaults
        for k, v in DEFAULT_CONFIG.items():
            if k not in cfg:
                cfg[k] = v
        return cfg
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return []

def save_log(log):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)

def load_queue():
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, "r") as f:
            return json.load(f)
    return []

def save_queue(queue):
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2)

def get_published_topics(site_id=None, niche_id=None):
    log = load_log()
    queue = load_queue()
    topics = set()
    for entry in log + queue:
        if site_id and entry.get("site_id") != site_id:
            continue
        if niche_id and entry.get("niche_id") != niche_id:
            continue
        topics.add(entry.get("topic", "").lower())
    return topics

# ─── AI call helpers ──────────────────────────────────────────────────────────

def call_groq(api_key, model, system_prompt, user_prompt):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }
    r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def call_gemini(api_key, model, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4000}
    }
    r = requests.post(url, json=payload, timeout=90)
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]

def call_mistral(api_key, model, system_prompt, user_prompt):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }
    r = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def call_openrouter(api_key, model, system_prompt, user_prompt):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://autoblogai.local"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }
    r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def call_anthropic(api_key, model, system_prompt, user_prompt):
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": model,
        "max_tokens": 4000,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}]
    }
    r = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=90)
    r.raise_for_status()
    return r.json()["content"][0]["text"]

def call_ollama(base_url, model, system_prompt, user_prompt):
    payload = {
        "model": model,
        "prompt": f"{system_prompt}\n\n{user_prompt}",
        "stream": False
    }
    r = requests.post(f"{base_url}/api/generate", json=payload, timeout=300)
    r.raise_for_status()
    return r.json()["response"]

def call_model(cfg, stage_key, system_prompt, user_prompt):
    pipeline = cfg["pipeline"]
    keys = cfg["api_keys"]
    stage = pipeline.get(stage_key, {})
    provider = stage.get("provider", "gemini")
    model = stage.get("model", "gemini-2.0-flash")

    if provider == "groq":
        return call_groq(keys["groq"], model, system_prompt, user_prompt)
    elif provider == "gemini":
        combined = f"{system_prompt}\n\n{user_prompt}"
        return call_gemini(keys["gemini"], model, combined)
    elif provider == "mistral":
        return call_mistral(keys["mistral"], model, system_prompt, user_prompt)
    elif provider == "openrouter":
        return call_openrouter(keys["openrouter"], model, system_prompt, user_prompt)
    elif provider == "anthropic":
        return call_anthropic(keys["anthropic"], model, system_prompt, user_prompt)
    elif provider == "ollama":
        return call_ollama(keys["ollama_url"], model, system_prompt, user_prompt)
    else:
        raise ValueError(f"Unknown provider: {provider}")

# ─── Sitemap fetcher ──────────────────────────────────────────────────────────

def fetch_sitemap_posts(sitemap_url):
    try:
        r = requests.get(sitemap_url, timeout=15)
        r.raise_for_status()
        import re
        urls = re.findall(r'<loc>(https?://[^<]+)</loc>', r.text)
        return urls[:50]  # cap at 50 for context length
    except Exception:
        return []

# ─── Amazon affiliate link builder ───────────────────────────────────────────

def build_amazon_link(product_name, associate_tag):
    if not associate_tag:
        return None
    query = product_name.replace(" ", "+")
    return f"https://www.amazon.com/s?k={query}&tag={associate_tag}"

# ─── Pipeline ─────────────────────────────────────────────────────────────────

def run_pipeline(niche, site, article_type_key, cfg, progress_cb=None):
    article_type = ARTICLE_TYPES.get(article_type_key, ARTICLE_TYPES["informational"])
    existing_topics = get_published_topics(site["id"], niche["id"])
    sitemap_posts = []
    if site.get("sitemap_url"):
        sitemap_posts = fetch_sitemap_posts(site["sitemap_url"])

    existing_str = "\n".join(list(existing_topics)[:30]) if existing_topics else "None yet"
    sitemap_str = "\n".join(sitemap_posts[:20]) if sitemap_posts else "No sitemap provided"

    # ── Stage 1: Strategist ──────────────────────────────────────────────────
    if progress_cb:
        progress_cb("Stage 1/6: Strategist finding topic...")

    s1_system = (
        "You are a content strategist. Your job is to identify high-value, SEO-friendly topics "
        "that have not been covered yet on this site. Return ONLY valid JSON, no markdown, no backticks."
    )
    s1_user = f"""
Niche: {niche['name']}
Description: {niche.get('description', '')}
Keywords: {niche.get('keywords', '')}
Article type: {article_type['name']} — {article_type['description']}
SEO focus: {article_type['seo_focus']}

Topics already published (avoid these):
{existing_str}

Return JSON:
{{
  "topic": "exact article title",
  "search_intent": "what problem does this solve and how do people search for it",
  "angle": "specific angle for this article type",
  "pain_points": ["pain point 1", "pain point 2", "pain point 3"],
  "outline_structure": ["section 1", "section 2", "section 3", "section 4"],
  "secondary_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5",
                         "keyword6", "keyword7", "keyword8", "keyword9", "keyword10"]
}}
"""
    s1_raw = call_model(cfg, "stage1_strategist", s1_system, s1_user)
    s1_raw = s1_raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    topic_data = json.loads(s1_raw)

    # ── Stage 2: Writer ──────────────────────────────────────────────────────
    if progress_cb:
        progress_cb("Stage 2/6: Writer drafting article...")

    internal_links_str = ""
    if sitemap_posts:
        internal_links_str = f"""
The site already has these published pages. Where naturally relevant, link to them:
{sitemap_str}
"""

    s2_system = (
        "You are a skilled content writer. Write human-first articles that teach from experience, "
        "not generic advice. Follow ALL formatting rules strictly."
    )
    s2_user = f"""
Topic: {topic_data['topic']}
Search intent: {topic_data['search_intent']}
Article type: {article_type['name']} — {article_type['tone']}
Angle: {topic_data['angle']}
Pain points to address: {', '.join(topic_data.get('pain_points', []))}
Outline: {', '.join(topic_data.get('outline_structure', []))}

STRICT WRITING RULES:
- Minimum 1,200 words
- Every paragraph must be at least 5 sentences
- NO unnecessary dashes — use commas or periods instead
- Natural, educational tone (human-first, not robotic)
- Teach based on experience, not generic advice
- Include a compelling intro that hooks immediately
- Use H2 and H3 subheadings
- End with a strong conclusion or call to action
{internal_links_str}

Write the complete article in HTML (use <h2>, <h3>, <p>, <ul>, <li> tags only). No preamble, just the article HTML.
"""
    draft_html = call_model(cfg, "stage2_writer", s2_system, s2_user)

    # ── Stage 3: Editor ──────────────────────────────────────────────────────
    if progress_cb:
        progress_cb("Stage 3/6: Editor refining draft...")

    s3_system = (
        "You are a tough editor. Your job is to challenge weak sections, cut fluff, "
        "improve clarity, and ensure the article delivers on its angle. "
        "Follow all formatting rules. Return only the improved HTML article."
    )
    s3_user = f"""
Article type: {article_type['name']}
Search intent: {topic_data['search_intent']}

EDITING RULES:
- Paragraphs must be 5+ sentences
- No unnecessary dashes — rewrite any sentences that use them
- Cut any generic filler phrases
- Strengthen weak arguments
- Ensure the angle ({topic_data['angle']}) is consistent throughout
- Maintain minimum 1,200 words

Original draft:
{draft_html}

Return only the improved HTML article, no commentary.
"""
    edited_html = call_model(cfg, "stage3_editor", s3_system, s3_user)

    # ── Stage 4: Curation / Quality Gate ────────────────────────────────────
    if progress_cb:
        progress_cb("Stage 4/6: Curation quality check...")

    s4_system = (
        "You are a quality control editor. Check the article against the rules and rewrite any "
        "sections that fail. Return ONLY the corrected HTML article."
    )
    s4_user = f"""
Check this article against ALL rules and fix any violations:

RULES TO ENFORCE:
1. Every paragraph must have 5+ sentences — rewrite short paragraphs to meet this
2. No unnecessary dashes in sentences — replace with commas or periods
3. Article must align with search intent: {topic_data['search_intent']}
4. Tone must match article type: {article_type['tone']}
5. Minimum 1,200 words
6. Human-first, educational, not robotic or generic

Article to curate:
{edited_html}

Return only the curated HTML article.
"""
    curated_html = call_model(cfg, "stage4_curator", s4_system, s4_user)

    # ── Stage 5: Metadata ────────────────────────────────────────────────────
    if progress_cb:
        progress_cb("Stage 5/6: Generating metadata...")

    associate_tag = site.get("associate_tag", "")
    amazon_note = ""
    if article_type_key == "monetization" and associate_tag:
        amazon_note = f"\nInclude 2-3 Amazon affiliate links in the content using this format: https://www.amazon.com/s?k=PRODUCT+NAME&tag={associate_tag}"

    s5_system = (
        "You are an SEO metadata specialist. Generate complete metadata based on the finalized article. "
        "Return ONLY valid JSON, no markdown, no backticks."
    )
    s5_user = f"""
Article topic: {topic_data['topic']}
Search intent: {topic_data['search_intent']}
Article type: {article_type['name']}
Secondary keywords already identified: {', '.join(topic_data.get('secondary_keywords', []))}
{amazon_note}

Generate metadata JSON:
{{
  "focus_keyphrase": "primary keyword phrase",
  "seo_title": "SEO optimized title under 60 chars",
  "slug": "url-friendly-slug",
  "meta_description": "compelling meta description under 155 chars",
  "meta_keywords": "comma separated list of 10-15 semantic keywords",
  "excerpt": "2-3 sentence excerpt for the post list",
  "categories": ["category1", "category2"],
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "image_prompt": "detailed prompt for generating featured image",
  "image_alt_text": "descriptive alt text for the featured image"
}}
"""
    s5_raw = call_model(cfg, "stage5_metadata", s5_system, s5_user)
    s5_raw = s5_raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    metadata = json.loads(s5_raw)

    # Inject Amazon links if monetization
    if article_type_key == "monetization" and associate_tag:
        for tag in metadata.get("tags", [])[:2]:
            link = build_amazon_link(tag, associate_tag)
            if link and link not in curated_html:
                curated_html += f'\n<p><a href="{link}" target="_blank" rel="nofollow">Check price on Amazon</a></p>'

    # ── Stage 6: Proofread ───────────────────────────────────────────────────
    if progress_cb:
        progress_cb("Stage 6/6: Final proofread...")

    s6_system = (
        "You are a final proofreader. Do a last pass for grammar, flow, and consistency. "
        "Return only the final polished HTML article."
    )
    s6_user = f"""
Do a final proofread. Fix any grammar issues, awkward phrasing, or flow problems.
Ensure the article reads naturally from start to finish.
Do NOT shorten the article or remove sections.

Article:
{curated_html}

Return only the final HTML article.
"""
    final_html = call_model(cfg, "stage6_proofread", s6_system, s6_user)

    return {
        "topic": topic_data["topic"],
        "content": final_html,
        "metadata": metadata,
        "topic_data": topic_data,
        "article_type": article_type_key,
        "site_id": site["id"],
        "niche_id": niche["id"],
        "site_url": site["url"],
        "niche_name": niche["name"],
        "status": "queued",
        "created_at": datetime.now().isoformat(),
        "id": f"post_{int(time.time())}"
    }

# ─── WordPress publisher ───────────────────────────────────────────────────────

def publish_to_wordpress(post_data, site):
    wp_url = site["url"].rstrip("/")
    username = site["wp_username"]
    app_password = site["wp_app_password"]
    author_id = site.get("wp_author_id", 1)

    token = base64.b64encode(f"{username}:{app_password}".encode()).decode("utf-8")
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }

    meta = post_data.get("metadata", {})

    payload = {
        "title": meta.get("seo_title", post_data["topic"]),
        "content": post_data["content"],
        "status": "publish",
        "slug": meta.get("slug", ""),
        "excerpt": meta.get("excerpt", ""),
        "author": author_id,
        "meta": {
            "meta_keywords": meta.get("meta_keywords", "")
        }
    }

    r = requests.post(f"{wp_url}/wp-json/wp/v2/posts", headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

# ─── Scheduler ────────────────────────────────────────────────────────────────

scheduler_running = False
scheduler_thread = None
pipeline_status = {}

def get_niche_interval_seconds(niche):
    posts_per_day = niche.get("posts_per_day", 1)
    return int(86400 / max(1, posts_per_day))

def get_article_type_for_niche(niche):
    mix = niche.get("article_type_mix", {})
    if not mix:
        return "informational"
    import random
    types = list(mix.keys())
    weights = [mix[t] for t in types]
    return random.choices(types, weights=weights, k=1)[0]

def scheduler_loop():
    global scheduler_running
    last_run = {}
    while scheduler_running:
        cfg = load_config()
        if not cfg.get("auto_publish"):
            time.sleep(30)
            continue

        for niche in cfg.get("niches", []):
            if not niche.get("active", True):
                continue
            niche_id = niche["id"]
            interval = get_niche_interval_seconds(niche)
            now = time.time()
            if now - last_run.get(niche_id, 0) < interval:
                continue

            site = next((s for s in cfg["sites"] if s["id"] == niche.get("site_id")), None)
            if not site:
                continue

            article_type = get_article_type_for_niche(niche)
            pipeline_status[niche_id] = {"running": True, "message": "Starting pipeline..."}

            try:
                def cb(msg, nid=niche_id):
                    pipeline_status[nid]["message"] = msg

                post_data = run_pipeline(niche, site, article_type, cfg, progress_cb=cb)

                if cfg.get("require_review", True):
                    queue = load_queue()
                    queue.append(post_data)
                    save_queue(queue)
                    pipeline_status[niche_id] = {"running": False, "message": "Added to review queue"}
                else:
                    wp_resp = publish_to_wordpress(post_data, site)
                    log = load_log()
                    post_data["status"] = "published"
                    post_data["wp_url"] = wp_resp.get("link", "")
                    log.append(post_data)
                    save_log(log)
                    pipeline_status[niche_id] = {"running": False, "message": f"Published: {post_data['topic']}"}

                last_run[niche_id] = now

            except Exception as e:
                pipeline_status[niche_id] = {"running": False, "message": f"Error: {str(e)}"}
                log = load_log()
                log.append({
                    "topic": niche.get("name", "unknown"),
                    "status": "error",
                    "error": str(e),
                    "site_id": site["id"],
                    "niche_id": niche_id,
                    "created_at": datetime.now().isoformat()
                })
                save_log(log)

        time.sleep(60)

# ─── API Routes ────────────────────────────────────────────────────────────────

@app.route("/api/config", methods=["GET"])
def get_config():
    cfg = load_config()
    safe = {k: v for k, v in cfg.items() if k != "api_keys"}
    safe["api_keys"] = {k: "***" if v and k != "ollama_url" else v
                        for k, v in cfg["api_keys"].items()}
    return jsonify(safe)

@app.route("/api/config", methods=["POST"])
def save_config_route():
    data = request.json
    cfg = load_config()
    if "api_keys" in data:
        for k, v in data["api_keys"].items():
            if v and v != "***":
                cfg["api_keys"][k] = v
    for field in ["pipeline", "auto_publish", "require_review"]:
        if field in data:
            cfg[field] = data[field]
    save_config(cfg)
    return jsonify({"success": True})

@app.route("/api/sites", methods=["GET"])
def get_sites():
    return jsonify(load_config().get("sites", []))

@app.route("/api/sites", methods=["POST"])
def save_sites():
    cfg = load_config()
    cfg["sites"] = request.json
    save_config(cfg)
    return jsonify({"success": True})

@app.route("/api/niches", methods=["GET"])
def get_niches():
    return jsonify(load_config().get("niches", []))

@app.route("/api/niches", methods=["POST"])
def save_niches():
    cfg = load_config()
    cfg["niches"] = request.json
    save_config(cfg)
    return jsonify({"success": True})

@app.route("/api/run", methods=["POST"])
def run_now():
    data = request.json
    niche_id = data.get("niche_id")
    article_type = data.get("article_type", "informational")

    cfg = load_config()
    niche = next((n for n in cfg["niches"] if n["id"] == niche_id), None)
    site = next((s for s in cfg["sites"] if s["id"] == niche.get("site_id")), None) if niche else None

    if not niche or not site:
        return jsonify({"error": "Niche or site not found"}), 404

    pipeline_status[niche_id] = {"running": True, "message": "Starting pipeline..."}

    def run():
        try:
            def cb(msg):
                pipeline_status[niche_id]["message"] = msg

            post_data = run_pipeline(niche, site, article_type, cfg, progress_cb=cb)

            if cfg.get("require_review", True):
                queue = load_queue()
                queue.append(post_data)
                save_queue(queue)
                pipeline_status[niche_id] = {"running": False, "message": "Added to review queue"}
            else:
                wp_resp = publish_to_wordpress(post_data, site)
                log = load_log()
                post_data["status"] = "published"
                post_data["wp_url"] = wp_resp.get("link", "")
                log.append(post_data)
                save_log(log)
                pipeline_status[niche_id] = {"running": False, "message": f"Published: {post_data['topic']}"}
        except Exception as e:
            pipeline_status[niche_id] = {"running": False, "message": f"Error: {str(e)}"}

    t = threading.Thread(target=run, daemon=True)
    t.start()
    return jsonify({"success": True, "message": "Pipeline started"})

@app.route("/api/status/<niche_id>", methods=["GET"])
def get_status(niche_id):
    return jsonify(pipeline_status.get(niche_id, {"running": False, "message": "Idle"}))

@app.route("/api/queue", methods=["GET"])
def get_queue():
    return jsonify(load_queue())

@app.route("/api/queue/<post_id>", methods=["GET"])
def get_queue_item(post_id):
    queue = load_queue()
    item = next((p for p in queue if p["id"] == post_id), None)
    if not item:
        return jsonify({"error": "Not found"}), 404
    return jsonify(item)

@app.route("/api/queue/<post_id>", methods=["PUT"])
def update_queue_item(post_id):
    queue = load_queue()
    idx = next((i for i, p in enumerate(queue) if p["id"] == post_id), None)
    if idx is None:
        return jsonify({"error": "Not found"}), 404
    queue[idx].update(request.json)
    save_queue(queue)
    return jsonify({"success": True})

@app.route("/api/queue/<post_id>/approve", methods=["POST"])
def approve_post(post_id):
    queue = load_queue()
    idx = next((i for i, p in enumerate(queue) if p["id"] == post_id), None)
    if idx is None:
        return jsonify({"error": "Not found"}), 404

    post_data = queue[idx]
    cfg = load_config()
    site = next((s for s in cfg["sites"] if s["id"] == post_data["site_id"]), None)
    if not site:
        return jsonify({"error": "Site not found"}), 404

    try:
        wp_resp = publish_to_wordpress(post_data, site)
        post_data["status"] = "published"
        post_data["wp_url"] = wp_resp.get("link", "")
        log = load_log()
        log.append(post_data)
        save_log(log)
        queue.pop(idx)
        save_queue(queue)
        return jsonify({"success": True, "wp_url": post_data["wp_url"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/queue/<post_id>/reject", methods=["DELETE"])
def reject_post(post_id):
    queue = load_queue()
    queue = [p for p in queue if p["id"] != post_id]
    save_queue(queue)
    return jsonify({"success": True})

@app.route("/api/log", methods=["GET"])
def get_log():
    return jsonify(load_log())

@app.route("/api/auto_publish", methods=["POST"])
def toggle_auto():
    cfg = load_config()
    cfg["auto_publish"] = request.json.get("enabled", False)
    save_config(cfg)
    global scheduler_running, scheduler_thread
    if cfg["auto_publish"] and not scheduler_running:
        scheduler_running = True
        scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        scheduler_thread.start()
    elif not cfg["auto_publish"]:
        scheduler_running = False
    return jsonify({"success": True, "auto_publish": cfg["auto_publish"]})

@app.route("/api/article_types", methods=["GET"])
def get_article_types():
    return jsonify(ARTICLE_TYPES)

@app.route("/api/test_site", methods=["POST"])
def test_site():
    site = request.json
    try:
        wp_url = site["url"].rstrip("/")
        token = base64.b64encode(f"{site['wp_username']}:{site['wp_app_password']}".encode()).decode()
        r = requests.get(f"{wp_url}/wp-json/wp/v2/users/me",
                         headers={"Authorization": f"Basic {token}"}, timeout=10)
        r.raise_for_status()
        user = r.json()
        return jsonify({"success": True, "user": user.get("name", "Connected")})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/test_ollama", methods=["POST"])
def test_ollama():
    url = request.json.get("url", "http://localhost:11434")
    try:
        r = requests.get(f"{url}/api/tags", timeout=5)
        models = [m["name"] for m in r.json().get("models", [])]
        return jsonify({"success": True, "models": models})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/stats", methods=["GET"])
def get_stats():
    log = load_log()
    queue = load_queue()
    today = datetime.now().date().isoformat()
    cfg = load_config()

    published = [e for e in log if e.get("status") == "published"]
    today_posts = [e for e in published if e.get("created_at", "").startswith(today)]

    per_site = {}
    for site in cfg.get("sites", []):
        sid = site["id"]
        per_site[sid] = {
            "name": site.get("name", site["url"]),
            "total": len([e for e in published if e.get("site_id") == sid]),
            "today": len([e for e in today_posts if e.get("site_id") == sid])
        }

    return jsonify({
        "total_published": len(published),
        "today": len(today_posts),
        "queued": len(queue),
        "errors": len([e for e in log if e.get("status") == "error"]),
        "per_site": per_site
    })

# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cfg = load_config()
    if cfg.get("auto_publish"):
        scheduler_running = True
        scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        scheduler_thread.start()
    print("\n  AutoBlog AI v3 is running.")
    print("  Open your browser: http://localhost:5000\n")
    app.run(debug=False, host="0.0.0.0", port=5000)

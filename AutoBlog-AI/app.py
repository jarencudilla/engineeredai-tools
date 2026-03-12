import os
import json
import time
import threading
import requests
import base64
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import re

def extract_json(text):
    """
    Safely extract JSON from LLM responses that may contain
    explanations, markdown, or extra text.
    """
    if not text:
        raise ValueError("Empty model response")

    text = text.strip()

    # remove markdown code fences
    text = text.replace("```json", "").replace("```", "")

    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ValueError(f"Could not locate JSON in response:\n{text[:500]}")

    try:
        return json.loads(match.group())
    except Exception as e:
        raise ValueError(f"Invalid JSON returned:\n{match.group()[:500]}") from e

app = Flask(__name__)
CORS(app)

CONFIG_FILE = "config.json"
LOG_FILE    = "posts_log.json"
QUEUE_FILE  = "review_queue.json"

DEFAULT_CONFIG = {
    "api_keys": {
        "gemini":     "",
        "groq":       "",
        "mistral":    "",
        "openrouter": "",
        "anthropic":  "",
        "ollama_url": "http://localhost:11434"
    },
    "pipeline": {
        "stage1_strategist": {"provider": "groq", "model": "llama-3.3-70b-versatile"},
        "stage2_writer":     {"provider": "groq", "model": "llama-3.3-70b-versatile"},
        "stage3_editor":     {"provider": "groq", "model": "llama-3.3-70b-versatile"},
        "stage4_curator":    {"provider": "groq", "model": "llama-3.3-70b-versatile"},
        "stage5_metadata":   {"provider": "groq", "model": "llama-3.3-70b-versatile"},
        "stage6_proofread":  {"provider": "groq", "model": "llama-3.3-70b-versatile"}
    },
    "sites":           [],
    "niches":          [],
    "auto_publish":    False,
    "require_review":  True
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

# ─── Config & Log helpers ─────────────────────────────────────────────────────

def load_config():
    """Load config.json as-is. Dashboard is the ONLY source of truth for pipeline config.
    DEFAULT_CONFIG is only used when config.json does not exist at all.
    Never overwrite existing values from config.json."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
        # Only fill top-level keys that are completely missing from config.json
        for k, v in DEFAULT_CONFIG.items():
            if k not in cfg:
                cfg[k] = v
        # Only add pipeline stages that are completely absent - never overwrite existing
        for stage_key, stage_val in DEFAULT_CONFIG["pipeline"].items():
            if stage_key not in cfg.get("pipeline", {}):
                cfg.setdefault("pipeline", {})[stage_key] = stage_val
        return cfg
    # No config.json exists at all - bootstrap from defaults
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
    log   = load_log()
    queue = load_queue()
    topics = set()
    for entry in log + queue:
        if site_id  and entry.get("site_id")  != site_id:  continue
        if niche_id and entry.get("niche_id") != niche_id: continue
        topics.add(str(entry.get("topic", "")).lower())
    return topics

# ─── AI call helpers ──────────────────────────────────────────────────────────

def _log_response_error(r, provider):
    """Print full API error response for debugging."""
    try:
        body = r.json()
    except Exception:
        body = r.text
    print(f"\n[{provider} ERROR] Status {r.status_code}")
    print(json.dumps(body, indent=2) if isinstance(body, dict) else body)
    print()

def _retry_on_rate_limit(fn, retries=1, wait=65):
    """Call fn(). On 429, wait and retry once."""
    for attempt in range(retries + 1):
        try:
            return fn()
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 429 and attempt < retries:
                print(f"[Rate limit] 429 received. Waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                raise

def call_groq(api_key, model, system_prompt, user_prompt):
    def _call():
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens":  4096
        }
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers, json=payload, timeout=90
        )
        if not r.ok:
            _log_response_error(r, "Groq")
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    return _retry_on_rate_limit(_call)

def call_gemini(api_key, model, prompt):
    def _call():
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={api_key}"
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4096}
        }
        r = requests.post(url, json=payload, timeout=120)
        if not r.ok:
            _log_response_error(r, "Gemini")
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    return _retry_on_rate_limit(_call)

def call_mistral(api_key, model, system_prompt, user_prompt):
    def _call():
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens":  4096
        }
        r = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers=headers, json=payload, timeout=90
        )
        if not r.ok:
            _log_response_error(r, "Mistral")
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    return _retry_on_rate_limit(_call)

def call_openrouter(api_key, model, system_prompt, user_prompt):
    def _call():
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://autoblogai.local"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens":  4096
        }
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers, json=payload, timeout=90
        )
        if not r.ok:
            _log_response_error(r, "OpenRouter")
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    return _retry_on_rate_limit(_call)

def call_anthropic(api_key, model, system_prompt, user_prompt):
    def _call():
        headers = {
            "x-api-key":         api_key,
            "anthropic-version": "2023-06-01",
            "content-type":      "application/json"
        }
        payload = {
            "model":      model,
            "max_tokens": 4096,
            "system":     system_prompt,
            "messages":   [{"role": "user", "content": user_prompt}]
        }
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers, json=payload, timeout=120
        )
        if not r.ok:
            _log_response_error(r, "Anthropic")
        r.raise_for_status()
        return r.json()["content"][0]["text"]
    return _retry_on_rate_limit(_call)

def call_ollama(base_url, model, system_prompt, user_prompt):
    payload = {
        "model":  model,
        "prompt": f"{system_prompt}\n\n{user_prompt}",
        "stream": False
    }
    r = requests.post(f"{base_url}/api/generate", json=payload, timeout=600)
    r.raise_for_status()
    return r.json()["response"]

def call_model(cfg, stage_key, system_prompt, user_prompt):
    """
    Route model calls with automatic fallback if a provider fails.
    """

    pipeline = cfg.get("pipeline", {})
    keys = cfg.get("api_keys", {})

    stage = pipeline.get(stage_key, DEFAULT_CONFIG["pipeline"].get(stage_key, {}))
    provider = stage.get("provider", "groq")
    model = stage.get("model", "llama-3.3-70b-versatile")

    print(f"[Pipeline] {stage_key} → {provider} / {model}")

    try:

        if provider == "groq":
            return call_groq(keys.get("groq", ""), model, system_prompt, user_prompt)

        elif provider == "gemini":
            combined = f"{system_prompt}\n\n{user_prompt}"
            return call_gemini(keys.get("gemini", ""), model, combined)

        elif provider == "mistral":
            return call_mistral(keys.get("mistral", ""), model, system_prompt, user_prompt)

        elif provider == "openrouter":
            return call_openrouter(keys.get("openrouter", ""), model, system_prompt, user_prompt)

        elif provider == "anthropic":
            return call_anthropic(keys.get("anthropic", ""), model, system_prompt, user_prompt)

        elif provider == "ollama":
            return call_ollama(
                keys.get("ollama_url", "http://localhost:11434"),
                model,
                system_prompt,
                user_prompt
            )

        else:
            raise ValueError(f"Unknown provider: {provider}")

    except Exception as e:

        print(f"[Pipeline ERROR] {stage_key} failed with {provider}: {e}")
        print("[Pipeline Fallback] Retrying with Groq")

        return call_groq(
            keys.get("groq", ""),
            "llama-3.3-70b-versatile",
            system_prompt,
            user_prompt
        )

# ─── Sitemap fetcher ──────────────────────────────────────────────────────────

def fetch_sitemap_posts(sitemap_url):
    try:
        r = requests.get(sitemap_url, timeout=15)
        r.raise_for_status()
        import re
        urls = re.findall(r'<loc>(https?://[^<]+)</loc>', r.text)
        return urls[:50]
    except Exception as e:
        print(f"[Sitemap] Failed to fetch {sitemap_url}: {e}")
        return []

# ─── Amazon affiliate link builder ───────────────────────────────────────────

def build_amazon_link(product_name, associate_tag):
    if not associate_tag:
        return None
    query = product_name.replace(" ", "+")
    return f"https://www.amazon.com/s?k={query}&tag={associate_tag}"

# ─── Pipeline ─────────────────────────────────────────────────────────────────

STAGE_DELAY = 3  # seconds between stages to avoid rate limit bursts

def run_pipeline(niche, site, article_type_key, cfg, progress_cb=None):
    article_type   = ARTICLE_TYPES.get(article_type_key, ARTICLE_TYPES["informational"])
    existing_topics = get_published_topics(site["id"], niche["id"])
    sitemap_posts  = []
    if site.get("sitemap_url"):
        sitemap_posts = fetch_sitemap_posts(site["sitemap_url"])

    existing_str = "\n".join(list(existing_topics)[:30]) if existing_topics else "None yet"
    sitemap_str  = "\n".join(sitemap_posts[:20]) if sitemap_posts else "No sitemap provided"

    # ── Stage 1: Strategist ──────────────────────────────────────────────────
    if progress_cb: progress_cb("Stage 1/6: Strategist finding topic...")

    s1_system = (
        "You are a content strategist. Identify high-value, SEO-friendly topics "
        "not yet covered on this site. Return ONLY valid JSON, no markdown, no backticks."
    )
    s1_user = f"""
Niche: {niche['name']}
Description: {niche.get('description', '')}
Keywords: {niche.get('keywords', '')}
Article type: {article_type['name']} - {article_type['description']}
SEO focus: {article_type['seo_focus']}

Topics already published (avoid these):
{existing_str}

Return this exact JSON structure:
{{
  "topic": "exact article title",
  "search_intent": "what problem does this solve and how do people search for it",
  "angle": "specific angle for this article type",
  "pain_points": ["pain point 1", "pain point 2", "pain point 3"],
  "outline_structure": ["section 1", "section 2", "section 3", "section 4"],
  "secondary_keywords": ["kw1","kw2","kw3","kw4","kw5","kw6","kw7","kw8","kw9","kw10"]
}}
"""
    s1_raw = call_model(cfg, "stage1_strategist", s1_system, s1_user)
    topic_data = extract_json(s1_raw)
    time.sleep(STAGE_DELAY)

    # ── Stage 2: Writer ──────────────────────────────────────────────────────
    if progress_cb: progress_cb("Stage 2/6: Writer drafting article...")

    internal_links_str = ""
    if sitemap_posts:
        internal_links_str = (
            f"\nINTERNAL LINKING RULES (STRICT):\n"
            f"- You MAY link to pages from this exact list only. Do NOT invent or guess any URLs.\n"
            f"- Use each URL a maximum of ONE time in the entire article.\n"
            f"- Only link when genuinely relevant to the sentence. Do not force links.\n"
            f"- Approved URLs:\n{sitemap_str}"
        )
    else:
        internal_links_str = "\nDo NOT add any internal links. No sitemap was provided."

    tone_override = niche.get("tone_override", "")
    tone_note = f"\nTone override for this site: {tone_override}" if tone_override else ""

    s2_system = (
        "You are a skilled content writer. Write human-first articles that teach from experience. "
        "Follow ALL formatting rules strictly. Return only the article body HTML. "
        "NEVER return a full HTML document. Do not include DOCTYPE, <html>, <head>, or <body> tags. "
        "Start your response directly with the first <h2> tag and nothing else."
    )
    s2_user = f"""
Topic: {topic_data['topic']}
Search intent: {topic_data['search_intent']}
Article type: {article_type['name']} - {article_type['tone']}
Angle: {topic_data['angle']}
Pain points: {', '.join(topic_data.get('pain_points', []))}
Outline: {', '.join(topic_data.get('outline_structure', []))}
{tone_note}

STRICT WRITING RULES:
- Minimum 1200 words
- Every paragraph must have at least 5 sentences
- NO unnecessary dashes, use commas or periods instead
- Natural educational tone, human-first not robotic
- Teach from experience, not generic advice
- Each paragraph must introduce NEW information. Never repeat concepts already covered.
- NEVER end a section with a transition like "In addition to our review..." or "We will also provide..." or "Furthermore we will discuss..." — these are filler. Cut them.
- NEVER use phrases like "we will provide", "we will discuss", "we will explore", "in addition to", "moreover", "furthermore" as sentence starters
- Write like a person, not a content robot. Specific, direct, useful.
- Compelling intro that hooks immediately
- Use H2 and H3 subheadings
- Strong conclusion or call to action
{internal_links_str}

OUTPUT FORMAT (CRITICAL):
- Return ONLY article body HTML
- NO DOCTYPE, NO <html>, NO <head>, NO <body> tags
- Start directly with the first <h2> tag
- Use only these tags: h2, h3, p, ul, li, a, strong
- No preamble, no explanation, just the article HTML
"""
    draft_html = call_model(cfg, "stage2_writer", s2_system, s2_user)
    time.sleep(STAGE_DELAY)

    # ── Stage 3: Editor ──────────────────────────────────────────────────────
    if progress_cb: progress_cb("Stage 3/6: Editor refining draft...")

    s3_system = (
        "You are a tough editor. Challenge weak sections, cut fluff, improve clarity. "
        "Ensure the article delivers on its angle. Return only the improved HTML article."
    )
    s3_user = f"""
Article type: {article_type['name']}
Search intent: {topic_data['search_intent']}
Angle to maintain: {topic_data['angle']}

EDITING RULES:
- Every paragraph must have 5 or more sentences
- No unnecessary dashes, rewrite any sentences that use them
- Cut generic filler phrases
- Strengthen weak arguments
- Minimum 1200 words maintained

Draft to edit:
{draft_html}

Return only the improved HTML article.
"""
    edited_html = call_model(cfg, "stage3_editor", s3_system, s3_user)

    # Safety strip: remove full HTML boilerplate if model returned a full document
    import re as _re
    if "<!DOCTYPE" in edited_html or "<html" in edited_html:
        body_match = _re.search(r'<body[^>]*>(.*?)</body>', edited_html, _re.DOTALL | _re.IGNORECASE)
        if body_match:
            edited_html = body_match.group(1).strip()
        else:
            edited_html = _re.sub(r'<(html|head|body|!DOCTYPE)[^>]*>', '', edited_html, flags=_re.IGNORECASE).strip()

    time.sleep(STAGE_DELAY)

    # ── Stage 4: Curator / Quality Gate ──────────────────────────────────────
    if progress_cb: progress_cb("Stage 4/6: Curator quality check...")

    s4_system = (
        "You are a quality control editor. Check the article against all rules and fix any violations. "
        "Return ONLY the corrected HTML article."
    )
    s4_user = f"""
Check and fix all violations:

RULES:
1. Every paragraph must have 5 or more sentences
2. No unnecessary dashes in sentences, replace with commas or periods
3. Article must align with search intent: {topic_data['search_intent']}
4. Tone must match: {article_type['tone']}
5. Minimum 1200 words
6. Human-first, educational, not robotic or generic

Article to curate:
{edited_html}

Return only the curated HTML article.
"""
    curated_html = call_model(cfg, "stage4_curator", s4_system, s4_user)

    # Safety strip: remove full HTML boilerplate if model returned a full document
    if "<!DOCTYPE" in curated_html or "<html" in curated_html:
        body_match = _re.search(r'<body[^>]*>(.*?)</body>', curated_html, _re.DOTALL | _re.IGNORECASE)
        if body_match:
            curated_html = body_match.group(1).strip()
        else:
            curated_html = _re.sub(r'<(html|head|body|!DOCTYPE)[^>]*>', '', curated_html, flags=_re.IGNORECASE).strip()

    time.sleep(STAGE_DELAY)

    # ── Stage 5: Metadata ─────────────────────────────────────────────────────
    if progress_cb: progress_cb("Stage 5/6: Generating SEO metadata...")

    associate_tag = site.get("associate_tag", "")
    amazon_note   = ""
    if article_type_key == "monetization" and associate_tag:
        amazon_note = (
            f"\nFor monetization articles, you must embed 2-3 Amazon affiliate links INLINE within the article content.\n"
            f"Place each link naturally within a relevant paragraph where a product recommendation makes sense.\n"
            f"Use descriptive anchor text matching the actual product (e.g. 'Fitbit Charge 5' not 'Check price on Amazon').\n"
            f"Build links using this format: https://www.amazon.com/s?k=PRODUCT+NAME&tag={associate_tag}\n"
            f"Replace PRODUCT+NAME with the actual product name using + for spaces.\n"
            f"Do NOT add a Resources section or dump links at the bottom."
        )

    s5_system = (
        "You are an SEO metadata specialist. Generate complete metadata for this article. "
        "Return ONLY valid JSON, no markdown, no backticks."
    )
    s5_user = f"""
Article topic: {topic_data['topic']}
Search intent: {topic_data['search_intent']}
Article type: {article_type['name']}
Secondary keywords: {', '.join(topic_data.get('secondary_keywords', []))}
{amazon_note}

Return this exact JSON:
{{
  "focus_keyphrase": "primary keyword phrase",
  "seo_title": "SEO title under 60 chars",
  "slug": "url-friendly-slug",
  "meta_description": "compelling meta description under 155 chars",
  "meta_keywords": "comma separated 10-15 semantic keywords",
  "excerpt": "2-3 sentence excerpt for post listings",
  "categories": ["category1"],
  "tags": ["tag1","tag2","tag3","tag4","tag5"],
  "image_prompt": "detailed prompt for featured image generation",
  "image_alt_text": "descriptive alt text for featured image"
}}
"""
    s5_raw = call_model(cfg, "stage5_metadata", s5_system, s5_user)
    metadata = extract_json(s5_raw)
    time.sleep(STAGE_DELAY)

    # Amazon links are now handled inline by Stage 2 writer prompt for monetization articles

    # ── Stage 6: Proofread ────────────────────────────────────────────────────
    if progress_cb: progress_cb("Stage 6/6: Final proofread...")

    s6_system = (
        "You are a final proofreader. Fix grammar, flow, and consistency issues. "
        "Do NOT shorten or remove sections. Return only the final HTML article."
    )
    s6_user = f"""
Final proofread pass. Fix grammar, awkward phrasing, and flow problems.
Ensure natural reading from start to finish.
Do NOT shorten or remove any sections.

Article:
{curated_html}

Return only the final HTML article.
"""
    final_html = call_model(cfg, "stage6_proofread", s6_system, s6_user)

    return {
        "topic":        topic_data["topic"],
        "content":      final_html,
        "metadata":     metadata,
        "topic_data":   topic_data,
        "article_type": article_type_key,
        "site_id":      site["id"],
        "niche_id":     niche["id"],
        "site_url":     site["url"],
        "niche_name":   niche["name"],
        "status":       "queued",
        "created_at":   datetime.now().isoformat(),
        "id":           f"post_{int(time.time())}"
    }

# ─── WordPress publisher ──────────────────────────────────────────────────────
def get_or_create_term_id(site, name, taxonomy):
    wp_url = site["url"].rstrip("/")
    username = site["wp_username"]
    password = site["wp_app_password"]

    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {"Authorization": f"Basic {token}", "Content-Type": "application/json"}

    # Try to find term
    r = requests.get(
        f"{wp_url}/wp-json/wp/v2/{taxonomy}?search={name}",
        headers=headers
    )
    r.raise_for_status()
    results = r.json()

    for term in results:
        if term["name"].lower() == name.lower():
            return term["id"]

    # Create if missing
    r = requests.post(
        f"{wp_url}/wp-json/wp/v2/{taxonomy}",
        headers=headers,
        json={"name": name}
    )
    r.raise_for_status()
    return r.json()["id"]

def get_site_categories(site):

    wp_url = site["url"].rstrip("/")
    username = site["wp_username"]
    password = site["wp_app_password"]

    token = base64.b64encode(f"{username}:{password}".encode()).decode()

    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }

    r = requests.get(
        f"{wp_url}/wp-json/wp/v2/categories?per_page=100",
        headers=headers
    )

    r.raise_for_status()

    return {c["name"]: c["id"] for c in r.json()}

def publish_to_wordpress(post_data, site):
    wp_url       = site["url"].rstrip("/")
    username     = site["wp_username"]
    app_password = site["wp_app_password"]
    author_id    = site.get("wp_author_id", 1)

    token   = base64.b64encode(f"{username}:{app_password}".encode()).decode("utf-8")
    headers = {"Authorization": f"Basic {token}", "Content-Type": "application/json"}
    meta    = post_data.get("metadata", {})
    site_categories = get_site_categories(site)

    categories = []
    for cat in meta.get("categories", []):
        if cat in site_categories:
            categories.append(site_categories[cat])

    tags = []
    for tag in meta.get("tags", []):
        tags.append(get_or_create_term_id(site, tag, "tags"))

    payload = {
    "title": meta.get("seo_title", post_data["topic"]),
    "content": post_data["content"],
    "status": "publish",
    "slug": meta.get("slug", ""),
    "excerpt": meta.get("excerpt", ""),
    "author": author_id,

    # Categories and tags
    "categories": categories,
    "tags": tags,

    # Yoast SEO + custom metadata
    "meta": {
        "_yoast_wpseo_title": meta.get("seo_title", ""),
        "_yoast_wpseo_metadesc": meta.get("meta_description", ""),
        "_yoast_wpseo_focuskw": meta.get("focus_keyphrase", ""),
        "meta_keywords": meta.get("meta_keywords", "")
    }
}

    r = requests.post(
        f"{wp_url}/wp-json/wp/v2/posts",
        headers=headers, json=payload, timeout=30
    )
    if not r.ok:
        _log_response_error(r, "WordPress")
    r.raise_for_status()
    return r.json()

# ─── Scheduler ────────────────────────────────────────────────────────────────

scheduler_running = False
scheduler_thread  = None
pipeline_status   = {}

def get_niche_interval_seconds(niche):
    posts_per_day = niche.get("posts_per_day", 1)
    return int(86400 / max(1, posts_per_day))

def get_article_type_for_niche(niche):
    mix = niche.get("article_type_mix", {})
    if not mix:
        return "informational"
    import random
    types   = list(mix.keys())
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
            now      = time.time()
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
                    pipeline_status[niche_id] = {
                        "running": False,
                        "message": f"Published: {post_data['topic']}"
                    }

                last_run[niche_id] = now

            except Exception as e:
                import traceback
                traceback.print_exc()
                pipeline_status[niche_id] = {"running": False, "message": f"Error: {str(e)}"}
                log = load_log()
                log.append({
                    "topic":      niche.get("name", "unknown"),
                    "status":     "error",
                    "error":      str(e),
                    "site_id":    site["id"],
                    "niche_id":   niche_id,
                    "created_at": datetime.now().isoformat()
                })
                save_log(log)

        time.sleep(60)

# ─── API Routes ───────────────────────────────────────────────────────────────

@app.route("/api/config", methods=["GET"])
def get_config():
    cfg  = load_config()
    safe = {k: v for k, v in cfg.items() if k != "api_keys"}
    safe["api_keys"] = {
        k: "***" if v and k != "ollama_url" else v
        for k, v in cfg["api_keys"].items()
    }
    return jsonify(safe)

@app.route("/api/config", methods=["POST"])
def save_config_route():
    data = request.json
    cfg  = load_config()
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
    data         = request.json
    niche_id     = data.get("niche_id")
    article_type = data.get("article_type", "informational")

    cfg   = load_config()
    niche = next((n for n in cfg["niches"] if n["id"] == niche_id), None)
    site  = next((s for s in cfg["sites"]  if s["id"] == niche.get("site_id")), None) if niche else None

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
                pipeline_status[niche_id] = {
                    "running": False,
                    "message": f"Published: {post_data['topic']}"
                }
        except Exception as e:
            import traceback
            traceback.print_exc()
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
    item  = next((p for p in queue if p["id"] == post_id), None)
    if not item:
        return jsonify({"error": "Not found"}), 404
    return jsonify(item)

@app.route("/api/queue/<post_id>", methods=["PUT"])
def update_queue_item(post_id):
    queue = load_queue()
    idx   = next((i for i, p in enumerate(queue) if p["id"] == post_id), None)
    if idx is None:
        return jsonify({"error": "Not found"}), 404
    queue[idx].update(request.json)
    save_queue(queue)
    return jsonify({"success": True})

@app.route("/api/queue/<post_id>/approve", methods=["POST"])
def approve_post(post_id):
    queue = load_queue()
    idx   = next((i for i, p in enumerate(queue) if p["id"] == post_id), None)
    if idx is None:
        return jsonify({"error": "Not found"}), 404

    post_data = queue[idx]
    cfg  = load_config()
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
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/queue/<post_id>/reject", methods=["DELETE"])
def reject_post(post_id):
    queue = [p for p in load_queue() if p["id"] != post_id]
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
        scheduler_thread  = threading.Thread(target=scheduler_loop, daemon=True)
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
        token  = base64.b64encode(
            f"{site['wp_username']}:{site['wp_app_password']}".encode()
        ).decode()
        r = requests.get(
            f"{wp_url}/wp-json/wp/v2/users/me",
            headers={"Authorization": f"Basic {token}"},
            timeout=10
        )
        r.raise_for_status()
        user = r.json()
        return jsonify({"success": True, "user": user.get("name", "Connected")})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/test_ollama", methods=["POST"])
def test_ollama():
    url = request.json.get("url", "http://localhost:11434")
    try:
        r      = requests.get(f"{url}/api/tags", timeout=5)
        models = [m["name"] for m in r.json().get("models", [])]
        return jsonify({"success": True, "models": models})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/stats", methods=["GET"])
def get_stats():
    log   = load_log()
    queue = load_queue()
    today = datetime.now().date().isoformat()
    cfg   = load_config()

    published   = [e for e in log if e.get("status") == "published"]
    today_posts = [e for e in published if e.get("created_at", "").startswith(today)]

    per_site = {}
    for site in cfg.get("sites", []):
        sid = site["id"]
        per_site[sid] = {
            "name":  site.get("name", site["url"]),
            "total": len([e for e in published   if e.get("site_id") == sid]),
            "today": len([e for e in today_posts if e.get("site_id") == sid])
        }

    return jsonify({
        "total_published": len(published),
        "today":           len(today_posts),
        "queued":          len(queue),
        "errors":          len([e for e in log if e.get("status") == "error"]),
        "per_site":        per_site
    })

# ─── Main ─────────────────────────────────────────────────────────────────────

def migrate_config():
    """One-time migrations on startup. Fixes known bad values and writes permanently to config.json.
    After this runs, dashboard is the sole source of truth. This never touches config at runtime."""
    if not os.path.exists(CONFIG_FILE):
        return
    cfg = load_config()
    changed = False
    decommissioned = {
    "mixtral-8x7b-32768": "llama-3.3-70b-versatile",
    "gemini-2.0-flash": "gemini-1.5-flash",
    "gemini-2.5-pro-preview": "gemini-1.5-pro"
}
    for stage_key, stage_val in cfg.get("pipeline", {}).items():
        if stage_val.get("model") in decommissioned:
            replacement = decommissioned[stage_val["model"]]
            print(f"[Migrate] {stage_key}: {stage_val['model']} → {replacement} (decommissioned)")
            cfg["pipeline"][stage_key]["model"] = replacement
            changed = True
    if changed:
        save_config(cfg)
        print("[Migrate] config.json updated. Dashboard now reflects correct models.")

if __name__ == "__main__":
    migrate_config()
    cfg = load_config()
    if cfg.get("auto_publish"):
        scheduler_running = True
        scheduler_thread  = threading.Thread(target=scheduler_loop, daemon=True)
        scheduler_thread.start()
    print("\n  AutoBlog AI v3.4 is running.")
    print("  Dashboard: http://localhost:5000\n")
    app.run(debug=False, host="0.0.0.0", port=5000)
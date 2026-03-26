import requests
from bs4 import BeautifulSoup
from readability import Document
import subprocess
import json

MODELS = ["llama3", "mistral"]

def fetch_page(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=15)
    res.raise_for_status()
    return res.text

def extract_content(html):
    doc = Document(html)
    soup = BeautifulSoup(doc.summary(), "html.parser")
    text = soup.get_text("\n")
    text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
    return text[:8000]

def run_ollama(prompt, model):
    proc = subprocess.Popen(
        ["ollama", "run", model],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = proc.communicate(prompt)
    return out.strip()

def run_with_fallback(prompt):
    for model in MODELS:
        try:
            out = run_ollama(prompt, model)
            json.loads(out)  # test valid JSON
            return out
        except:
            continue
    return None

def build_prompt(content):
    return f"""
You are a tactical content analyst.

Content:
\"\"\"
{content}
\"\"\"

TASK:
1. Summarize the main argument in 2-3 sentences.
2. Identify a missing angle / nuance.
3. Identify a weak assumption or limitation.

Generate 3 comment drafts:
- Comment 1 (Extension)
- Comment 2 (Constraint)
- Comment 3 (Application)

Rules:
- No praise or fluff
- No emojis
- Max 120 words per comment
- Output strict JSON:

{{
  "summary": "...",
  "gap": "...",
  "weakness": "...",
  "comments": [
    "...",
    "...",
    "..."
  ]
}}
"""

def analyze_url(url):
    html = fetch_page(url)
    content = extract_content(html)
    prompt = build_prompt(content)
    raw = run_with_fallback(prompt)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except:
        print(raw)
        return None
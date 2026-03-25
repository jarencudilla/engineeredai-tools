# Comment Intelligence Dashboard

A local **Flask + Ollama-powered dashboard** for discovering relevant blogs, analyzing content, and generating actionable comment drafts.

Built for **content-aware presence**, not automation spam. You stay in control of posting.

---

## Features

- Auto-discover blogs using seed site + keywords  
- Scrape article content (cleaned main body)  
- Analyze content using local LLM (no API cost)  
- Generate 3 comment drafts per post:
  - Extension (adds missing angle)
  - Constraint (challenges assumption)
  - Application (practical use case)
- Dashboard queue for review/edit/post
- Status tracking: `new → ready → posted`
- Fully local (no paid APIs required)

---

## Workflow

```
[Seed Site / Topic]
        ↓
 Auto Discovery (Google / RSS)
        ↓
   Filter (Recent / Relevant)
        ↓
 Scrape Content (Article Text)
        ↓
 Local LLM (Ollama)
        ↓
 Summary + Gap + Comments
        ↓
 Dashboard Queue → Review → Post
```

---

## Requirements

- Python 3.10+
- Ollama (local LLM runtime)
- SQLite (included with Python)

Python libraries:
- Flask
- requests
- beautifulsoup4
- readability-lxml

---

## Installation

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd comment-intel
```

### 2. Create virtual environment

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize database

```bash
python -c "from db import init_db; init_db()"
```

### 5. Install Ollama and pull models

Install Ollama from:
https://ollama.com

Then run:

```bash
ollama pull llama3
ollama pull mistral
```

---

## Running the App

```bash
python app.py
```

Open in browser:

http://127.0.0.1:5000

---

## Usage

### 1. Add URLs manually
Paste a blog URL → click **Add URL**

### 2. Auto-discover blogs
Enter:
- Seed site (e.g. `engineeredai.net`)
- Topic keywords

Click **Discover URLs**

### 3. Process content
Click **Process** on any URL:
- Scrapes article
- Runs LLM analysis
- Generates:
  - Summary
  - Gap
  - Weakness
  - 3 comment drafts

### 4. Review comments
- Edit drafts directly in dashboard
- Copy and post manually
- Click **Mark Posted** when done

---

## Database Schema

```
comments
- id
- url
- summary
- gap
- weakness
- comment1
- comment2
- comment3
- status (new / ready / posted)
- date_added
```

---

## Design Principles

- No auto-posting (manual control only)
- No API dependency (fully local)
- AI assists thinking, not presence
- Focus on relevance over volume

---

## Optional Enhancements

- Batch processing (process multiple URLs)
- RSS feed discovery (Dev.to, Medium, etc.)
- Domain tracking (avoid repetition)
- Comment scoring (engagement likelihood)
- Copy-to-clipboard buttons

---

## Notes

- Some sites block scraping — expected behavior
- Google scraping may rate-limit if abused
- LLM output depends on model quality (llama3 recommended)

---

## License

MIT License

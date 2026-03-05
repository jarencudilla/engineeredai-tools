# AutoBlog AI v3 — Setup Guide

## What This Is

An autonomous AI writing engine. You configure it with sites and niches, it finds topics, writes full articles through a 6-stage multi-model pipeline, and publishes them to your WordPress sites. Alfred and Edwin do the work.

---

## Step 1 — Install Python

1. Go to **https://python.org/downloads**
2. Download Python 3.12 (or latest 3.x)
3. Run the installer
4. **CRITICAL: Check "Add Python to PATH"** before clicking Install
5. Click Install Now

Verify it worked: open PowerShell and type `python --version`  
You should see `Python 3.12.x`

---

## Step 2 — Run the App

1. Put all 5 files in one folder (e.g. `C:\AutoBlogAI\`)
2. Double-click `start.bat`
3. A terminal window opens and installs dependencies automatically
4. Your browser opens at `http://localhost:5000`

That's it. Leave the terminal window open — it's the server.

---

## Step 3 — Get Your Free API Keys

You need at least **one** of these to generate content. Start with Groq + Gemini.

### Groq (Free — Recommended for drafting)
1. Go to **https://console.groq.com**
2. Sign up with Google or email
3. Click API Keys → Create API Key
4. Copy the key starting with `gsk_`
5. Paste into Settings → Groq

**Free limits:** Very generous. ~14,400 tokens/minute. More than enough.

### Gemini (Free — Recommended for writing quality)
1. Go to **https://aistudio.google.com**
2. Sign in with your Google account
3. Click "Get API Key" → Create API Key
4. Copy the key starting with `AIza`
5. Paste into Settings → Google Gemini

**Free limits:** Gemini 2.0 Flash = 1,500 requests/day. Each article uses ~6 calls. That's ~250 articles/day free.

### Mistral (Free tier)
1. Go to **https://console.mistral.ai**
2. Sign up → Go to API Keys
3. Create and copy your key
4. Paste into Settings → Mistral AI

### OpenRouter (Free models available)
1. Go to **https://openrouter.ai/keys**
2. Sign up → Create API Key
3. Paste into Settings → OpenRouter
4. Free models available: Llama 3.3, Gemma 3, Phi-4, DeepSeek R1

### Ollama (Completely free — runs locally on your PC)
1. Go to **https://ollama.com/download** → Download for Windows
2. Install it (it runs as a background service)
3. Open PowerShell and run:
   ```
   ollama pull phi4
   ollama pull mistral
   ollama pull gemma3
   ```
4. In Settings, click "Test Connection" — it will show your installed models
5. **Note for Legion 5 (RTX 3050 Ti 4GB):** Use phi4, mistral:7b-q4, or gemma3:4b. Larger models will be very slow.

### Claude / Anthropic (Paid — best quality)
1. Go to **https://console.anthropic.com**
2. Sign up (separate from claude.ai — different product)
3. Add a credit card and purchase credits ($5 to start)
4. Go to API Keys → Create Key starting with `sk-ant-`
5. Paste into Settings → Anthropic Claude
6. **Cost:** ~$0.03–0.08 per full article with Sonnet 4.6

---

## Step 4 — Set Up WordPress AI Authors

Do this for each WordPress site you want to post to.

### Create the AI Author Account
1. Login to your WordPress admin
2. Go to Users → Add New
3. Fill in:
   - **Username:** `alfred` or `edwin`
   - **Email:** any valid email (alfred@yourdomain.com works)
   - **Role:** Author
4. Save the user
5. Note the User ID (check the URL when editing: `user_id=X`)

### Generate Application Password
1. Edit the alfred/edwin user
2. Scroll down to **Application Passwords**
3. In the "New Application Password Name" field type: `AutoBlog AI`
4. Click **Add New Application Password**
5. **Copy the password immediately** — it won't show again
6. Format: `xxxx xxxx xxxx xxxx xxxx xxxx`

---

## Step 5 — Add Your Sites in the Dashboard

1. Open the dashboard at `http://localhost:5000`
2. Click **Sites** in the sidebar
3. Click **+ Add Site**
4. Fill in:
   - **Site Name:** Friendly name (e.g. "Healthy Forge")
   - **WordPress URL:** Full URL with https (e.g. `https://healthyforge.com`)
   - **AI Author Username:** `alfred` (exactly as you created it)
   - **Application Password:** The password you copied
   - **Author User ID:** The numeric ID from the URL
   - **Amazon Associate Tag:** e.g. `healthyforge-20` (leave blank if none)
   - **Post Sitemap URL:** e.g. `https://healthyforge.com/post-sitemap.xml` (for internal linking)
5. Click **Test WordPress Connection** — should show ✓ Connected
6. Click **Save Site**

Repeat for each site.

---

## Step 6 — Add Niches

1. Click **Niches** in the sidebar
2. Click **+ Add Niche**
3. Fill in:
   - **Niche Name:** e.g. "Health & Fitness"
   - **Assign to Site:** Select from your added sites
   - **Description:** What this niche covers (be specific — this guides topic generation)
   - **Target Keywords:** Comma separated keywords to focus on
   - **Posts Per Day:** Start with **1** for safety
   - **Article Type Mix:** Set percentages (should add to 100)
4. Click **Save Niche**

**Recommended starting mix:**
- Informational: 50%
- Viral: 25%
- Monetization: 25%

---

## Step 7 — Configure Pipeline Models

1. Click **Pipeline** in the sidebar
2. For each stage, select provider and model
3. **Recommended free stack:**
   - Stage 1 Strategist: Groq → llama-3.3-70b-versatile
   - Stage 2 Writer: Gemini → gemini-2.5-pro-preview-06-05
   - Stage 3 Editor: Groq → mixtral-8x7b-32768
   - Stage 4 Curator: Gemini → gemini-2.0-flash
   - Stage 5 Metadata: Gemini → gemini-2.5-pro-preview-06-05
   - Stage 6 Proofread: Groq → llama-3.3-70b-versatile
4. Click **Save Pipeline Config**

---

## Step 8 — Test Run

1. Go to **Command Center**
2. Find your niche in the Niche Runner section
3. Select article type from the dropdown
4. Click **▶ Run Now**
5. Watch the status update every 2 seconds
6. Pipeline takes 3–5 minutes to complete

If **Require Review** is ON (recommended to start):
- Draft goes to Review Queue
- Go to **Review Queue** to see it
- Click **✎ Edit** to edit the content and metadata
- Click **✓ Approve** to publish, or **✕** to discard

---

## Step 9 — Enable Auto-Publish

Once you've verified the output quality:
1. Use the **Auto-Publish** toggle in the bottom-left sidebar
2. The scheduler fires every 60 seconds, checks which niches are due, and runs them

Posting frequency is based on your "Posts Per Day" per niche. 1x/day = runs once every 24 hours.

---

## Files Reference

| File | Purpose |
|------|---------|
| `app.py` | Backend server, pipeline, scheduler, WordPress publisher |
| `index.html` | Dashboard UI |
| `start.bat` | Windows launcher — double-click to run |
| `requirements.txt` | Python packages |
| `config.json` | Your settings (auto-created, DO NOT share publicly) |
| `posts_log.json` | History of all published posts |
| `review_queue.json` | Drafts waiting for approval |
| `SETUP.md` | This file |

---

## Troubleshooting

**start.bat opens and closes immediately**  
Python is not in PATH. Reinstall Python and check "Add Python to PATH".

**Dashboard doesn't open**  
Open browser manually and go to `http://localhost:5000`

**WordPress connection fails**  
- Check the URL includes `https://`
- Make sure the Application Password has no extra spaces
- Verify the username matches exactly (case-sensitive)
- Check the author role is at least "Author"

**Pipeline returns error**  
- Check Settings — at least one API key must be configured for each stage's provider
- Check the terminal window for the full error message

**Ollama not connecting**  
- Make sure Ollama is running (check system tray or run `ollama serve` in PowerShell)
- Default URL is `http://localhost:11434`
- Pull at least one model first: `ollama pull phi4`

**Posts going out in wrong language / low quality**  
- Increase the description detail in your niche config
- Try a different model for Stage 2 (Writer) — Gemini 2.5 Pro produces the best results
- Check if the article type mix makes sense for the niche

---

## Keeping Your Account Safe

- Alfred and Edwin post under their own accounts
- Your admin account is never used for publishing
- config.json contains your API keys — do NOT share or commit it to GitHub
- Add `config.json`, `posts_log.json`, `review_queue.json` to `.gitignore` if you ever version control this

---

## Amazon Affiliate Notes

**Mode 1 (current):** AI generates search-based links using your Associate tag. Format: `amazon.com/s?k=PRODUCT+NAME&tag=yourtag-20`. Works immediately, no API needed.

**Mode 2 (when you have 3+ qualifying sales):** Apply for Product Advertising API access inside Amazon Associates dashboard. Once approved, add credentials to the app for exact ASIN-based product links.

Associate tags are set per site. Create separate tracking IDs in Amazon Associates for each site so you know which one converts.

---

## Experiment Log Notes

Since this is a live experiment, track:
- Article quality on first run (spot check)
- Google Search Console indexing status at Day 7 and Day 14
- Amazon affiliate click data per site
- Any manual edits you make in the review queue
- Which article types perform better on which niches

That data is the EAI post series.

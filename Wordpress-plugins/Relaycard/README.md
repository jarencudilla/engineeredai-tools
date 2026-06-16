=== RelayCard ===
Contributors: engineeredai
Tags: related posts, inline related posts, content cards, post cards, internal linking
Requires at least: 6.0
Tested up to: 6.7
Requires PHP: 8.0
Stable tag: 1.0.1
License: GPLv2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

Inline post cards that read like ads, link like content. Image-dominant related post cards injected automatically into your content.

== Description ==

**RelayCard** automatically injects image-dominant related post cards inside your content — heading-aware, config-driven, and designed to look like premium editorial ad units.

Unlike traditional related posts plugins that dump links at the bottom of your post (where nobody reads), RelayCard places cards *inside* your content at the right moment — after enough context has been built, before the next section begins. The result is a visual break that keeps readers in your ecosystem instead of bouncing.

**Why RelayCard is different:**

* **Image-dominant by design** — the image stops the scroll, the title closes the click
* **Heading-aware injection** — counts H2/H3/H4s and scales card placement automatically. Short posts get 1 card, long posts get 2. Nothing gets forced.
* **5 card styles** — Split, Overlay, Cinematic, Minimal, Story
* **3 font categories** — Sans-serif, Monospace, Script
* **3 image ratio presets** — 50/50, 60/40, 70/30
* **AI hook title generation** — optional BYOK (Gemini, ChatGPT, Claude). Rewrites post titles into punchy hook titles automatically.
* **Card title custom field** — override the title per post with your own hook
* **SEO plugin aware** — detects RankMath, Yoast, AIOSEO titles automatically
* **Live admin preview** — see your card render in real time before saving
* **Zero setup friction** — CSS auto-enqueues on activation, no shortcodes needed
* **Featured images required** — cards only fire when a post has a featured image, keeping quality high

**Card Title Priority Stack:**
1. `card_title` custom field (manual override)
2. SEO plugin title (RankMath → Yoast → AIOSEO)
3. AI generated hook title (optional, BYOK)
4. Post title (always available fallback)

**Card Styles:**
* **Split** — image left, text right. Classic editorial card.
* **Overlay** — full bleed image with gradient overlay and title on top. High visual impact.
* **Cinematic** — wide image, centered title overlay. Maximum eye candy.
* **Minimal** — no image, styled text card with accent border. Clean and fast.
* **Story** — image top, text below. Mobile-first vertical layout.

**AI Hook Title Generation (optional):**
Bring your own API key from any of these providers:
* Gemini (Google AI Studio — free tier available)
* ChatGPT (OpenAI)
* Claude (Anthropic)

No key required. Cards work without AI. AI just makes the titles punchier.

== Installation ==

1. Upload the `relaycard` folder to `/wp-content/plugins/`
2. Activate the plugin through the Plugins screen in WordPress
3. Go to **Settings → RelayCard** to configure your card style, colors, and optional AI title generation
4. Cards will automatically appear in single posts with 4 or more headings and featured images

== Frequently Asked Questions ==

= Does RelayCard work without AI? =
Yes. AI hook title generation is completely optional. Cards fire on all qualifying posts using the post title (or SEO title if a plugin is detected) as the card title.

= What counts as a qualifying post? =
A post must have at least 4 headings (H2, H3, or H4) and a featured image for cards to fire. Posts with fewer headings or no featured image are skipped.

= How many cards appear per post? =
Posts with 4-5 headings get 1 card. Posts with 6 or more headings get 2 cards. The plugin scales automatically — nothing is hardcoded.

= Where exactly do the cards inject? =
Cards inject *before* trigger headings — not after them. This means the card acts as a visual break between sections, not a disruption right after a heading. Mid-content, between sections, exactly where a reader pauses.

= Can I set a custom title per card? =
Yes. Add a custom field named `card_title` to any post. That value takes priority over everything else including AI generation.

= Which SEO plugins does RelayCard detect? =
RankMath, Yoast SEO, and All in One SEO (AIOSEO) — checked in that order.

= Will RelayCard slow down my site? =
No. The related posts query uses `no_found_rows` and `ignore_sticky_posts` for performance. CSS is only enqueued on single post pages. AI title generation uses a short 8-second timeout and fails gracefully with no impact on page load.

= Does RelayCard add nofollow to links? =
Cards link to your own posts — these are internal links and do not need nofollow. The attribution link to engineeredai.net is a standard dofollow link.

= Can I remove the attribution? =
The attribution (`// built with RelayCard — engineeredai.net`) is present on the free version and cannot be removed. It is minimal, monospace, and low-opacity — most readers won't notice it. A premium version with attribution removal may be available in the future.

== Screenshots ==

1. Split style card — image left, text right, inside post content
2. Overlay style card — full bleed with gradient and title overlay
3. Cinematic style card — wide image with centered title
4. Minimal style card — no image, accent border, clean text
5. Story style card — vertical layout, image top
6. Admin settings page with live preview panel
7. Style picker with visual card thumbnails

== Changelog ==

= 1.0.0 =
* Initial release
* 5 card styles: Split, Overlay, Cinematic, Minimal, Story
* Heading-aware automatic injection (H2/H3/H4)
* Dynamic card count: 1 card for 4-5 headings, 2 cards for 6+
* Card title priority stack: custom field → SEO plugin → AI → post title
* AI hook title generation: Gemini, ChatGPT, Claude (BYOK)
* 3 font categories: Sans-serif, Monospace, Script
* 3 image ratio presets: 50/50, 60/40, 70/30
* Accent color picker
* Live admin preview panel
* CSS auto-enqueued on single posts only
* SEO plugin detection: RankMath, Yoast, AIOSEO
* Attribution: // built with RelayCard — engineeredai.net

= 1.0.1 =
* Updated enqueue styles

== Upgrade Notice ==

= 1.0.0 =
Initial release.
= 1.0.1 =
Relaycard Stable

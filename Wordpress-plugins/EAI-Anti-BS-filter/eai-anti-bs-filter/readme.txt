=== EAI Anti-BS Filter ===
Contributors: engineeredai
Tags: comments, spam, anti-spam, moderation, humor
Requires at least: 6.0
Tested up to: 6.6
Requires PHP: 8.0
Stable tag: 1.0.0
License: GPLv2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

Sanitizes spam comments instead of deleting them — replaces the name, email, and content with a roast, and learns from confirmed spam over time.

== Description ==

Most anti-spam plugins delete spam silently. EAI Anti-BS Filter keeps the comment slot but replaces the author name, email, and content with a randomly-picked "roast" line and persona, so the spam attempt becomes a small joke instead of disappearing without a trace.

**How detection works**

The plugin scores each comment against several weighted signals (free-mail patterns, finance/crypto keywords, referral-link patterns, templated spam phrasing, and a learned fingerprint database). A comment is only sanitized once it crosses a combined threshold — no single weak signal triggers it on its own.

Pingbacks and trackbacks are never sanitized.

**Manual control**

Every comment row gets a "🔥 Roast" and "✅ Not Spam" action alongside WordPress's native Spam/Trash links, so you stay in control and the plugin learns from your calls either way.

**Learning**

The fingerprint database trains only from comments WordPress has confirmed as spam (never from held/pending comments), on an hourly schedule plus on activation and on every manual roast.

= Lite vs Pro =

The Lite version includes a small linked credit ("Sanitized by EAI Anti-BS Bot™") in the roast footer. Enabling Pro mode in Settings removes the link.

== Installation ==

1. Upload the plugin files to `/wp-content/plugins/eai-anti-bs-filter`, or install via the WordPress Plugins screen.
2. Activate the plugin.
3. Visit Settings → EAI Anti-BS Filter to review auto-approve, Pro mode, and the roast persona/line pools.

== Frequently Asked Questions ==

= Will this delete my comments? =

No. It replaces the visible name, email, and content of confirmed spam — the comment slot stays, the spam doesn't.

= Will it sanitize pingbacks or legitimate held comments? =

No. Pingbacks/trackbacks are hard-excluded, and detection always runs its own scoring check rather than trusting WordPress's held/spam status alone.

= What if it sanitizes something by mistake? =

Use Tools → 🔄 Recover Sanitized to restore any comment the plugin has sanitized, using the original content it saved before sanitizing.

== Changelog ==

= 1.0.0 =
* Rebuilt detection as a scored multi-signal model instead of single-signal matching.
* Fixed: pingbacks/trackbacks and legitimate held comments were being sanitized — detector now re-verifies every comment instead of trusting WordPress's held/spam status.
* Fixed: fingerprint training no longer learns from held (non-confirmed-spam) comments.
* Consolidated fingerprint extraction into a single source of truth.
* Added manual "Not Spam" action alongside manual "Roast".
* Split pingback recovery into its own admin tool.

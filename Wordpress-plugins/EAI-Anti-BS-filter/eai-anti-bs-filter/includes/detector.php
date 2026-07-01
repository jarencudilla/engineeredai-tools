<?php
/**
 * includes/detector.php
 *
 * The ONE place spam-or-not gets decided. Every hook that can sanitize a
 * comment (preprocess, transition-to-spam, direct-insert-as-spam) must call
 * eai_abs_is_spam() — never act on WordPress's own held/spam status alone,
 * since WP holds plenty of legitimate comments (first-timers, link-bearing
 * replies) and routinely holds pingbacks too.
 *
 * Detection is a SCORED model, not "any one signal triggers it" — single
 * weak signals (a free-mail address, one generic compliment) are common in
 * genuine comments. It takes a combination to flag.
 *
 * Depends on: fingerprint-matcher.php (eai_abs_get_fingerprints).
 * Called from: sanitizer.php.
 */
defined('ABSPATH') || exit;

const EAI_ABS_SPAM_THRESHOLD = 3;

/**
 * eai_abs_is_pingback_or_trackback
 * Hard exclusion check. Pingbacks/trackbacks are never sanitized by this
 * plugin — WordPress's own pingback handling / Akismet owns that.
 * @param  array|WP_Comment $comment
 * @return bool
 */
function eai_abs_is_pingback_or_trackback($comment) {
    $type = is_array($comment)
        ? ($comment['comment_type'] ?? 'comment')
        : ($comment->comment_type ?? 'comment');
    return in_array($type, ['pingback', 'trackback'], true);
}

/**
 * eai_abs_is_spam
 * Score a comment against weighted signals; flag as spam only at/above
 * EAI_ABS_SPAM_THRESHOLD. Never called on pingbacks/trackbacks — caller
 * should exclude those before reaching here, but this function defends
 * against it too in case it's called directly.
 * @param  array|WP_Comment $comment
 * @return bool
 */
function eai_abs_is_spam($comment) {
    if (eai_abs_is_pingback_or_trackback($comment)) {
        return false;
    }

    $get = function ($key) use ($comment) {
        return is_array($comment) ? ($comment[$key] ?? '') : ($comment->$key ?? '');
    };

    $content = strtolower((string) $get('comment_content'));
    $email   = strtolower((string) $get('comment_author_email'));
    $url     = strtolower((string) $get('comment_author_url'));

    $score   = 0;
    $matched = [];

    // Free throwaway-style mail (outlook.com numeric-handle pattern seen in
    // confirmed spam history) — weak alone, contributes partial weight.
    if ($email && preg_match('/^\d{5,}@outlook\.com$/', $email)) {
        $score += 2;
        $matched[] = 'throwaway_outlook_pattern';
    }

    // Finance/crypto/referral keyword in content or URL.
    $finance_kw = ['binance', 'gate.io', 'gate.com', 'usdt', 'crypto', 'forex', 'casino', 'loan', 'betting'];
    foreach ($finance_kw as $kw) {
        if (strpos($content . ' ' . $url, $kw) !== false) {
            $score += 2;
            $matched[] = 'finance_keyword:' . $kw;
            break; // one hit is enough signal, don't stack duplicates
        }
    }

    // Referral/registration link pattern.
    if (preg_match('/ref=|register\?|signup\?ref/i', $content . ' ' . $url)) {
        $score += 2;
        $matched[] = 'referral_link_pattern';
    }

    // Templated generic-praise/question phrasing seen repeatedly in spam log.
    // Requires the FULL templated shape, not isolated words like "thanks" —
    // narrowed specifically to avoid catching real reader comments.
    $templated = [
        '/thank you for your sharing\. i am worried that i lack creative ideas/i',
        '/your article helped me a lot, is there any more related content/i',
        '/i read many of your blog posts, cool, your blog is very good/i',
        '/your point of view caught my eye and was very interesting.*i have a question for you/i',
        '/i don.t think the title of your article matches the content lol/i',
        '/can you be more specific about the content of your article.*hope you can help me/i',
        '/reading your article has greatly helped me.*i will pay attention to your answer/i',
    ];
    foreach ($templated as $pattern) {
        if (preg_match($pattern, $content)) {
            $score += 2;
            $matched[] = 'templated_phrase';
            break;
        }
    }

    // 2+ links in a comment body is unusual for genuine reader comments.
    if (preg_match_all('#https?://#i', $content) >= 2) {
        $score += 1;
        $matched[] = 'multiple_links';
    }

    // Learned fingerprints (trained from confirmed spam only).
    $fp = eai_abs_get_fingerprints();
    foreach ($fp['keywords'] ?? [] as $kw) {
        if ($kw && strpos($content . ' ' . $url, $kw) !== false) {
            $score += 1;
            $matched[] = 'fp_keyword:' . $kw;
            break;
        }
    }
    foreach ($fp['domains'] ?? [] as $d) {
        if ($d && strpos($content . ' ' . $url, $d) !== false) {
            $score += 1;
            $matched[] = 'fp_domain:' . $d;
            break;
        }
    }
    if ($email && strpos($email, '@') !== false) {
        $email_domain = substr($email, strpos($email, '@') + 1);
        if (in_array($email_domain, $fp['emails'] ?? [], true)) {
            $score += 1;
            $matched[] = 'fp_email_domain:' . $email_domain;
        }
    }

    $is_spam = $score >= EAI_ABS_SPAM_THRESHOLD;

    if (EAI_ABS_DEBUG) {
        error_log(sprintf(
            '[EAI] score=%d threshold=%d spam=%s signals=[%s]',
            $score, EAI_ABS_SPAM_THRESHOLD, $is_spam ? 'yes' : 'no', implode(', ', $matched)
        ));
    }

    return $is_spam;
}

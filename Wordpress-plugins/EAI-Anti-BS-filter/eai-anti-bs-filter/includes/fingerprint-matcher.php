<?php
/**
 * includes/fingerprint-matcher.php
 *
 * Sole owner of the learned-spam-pattern database (keywords, domains, email
 * domains). Trains from confirmed spam only — never from held/pending
 * comments, and never from pingbacks/trackbacks, since both produce false
 * signal (legitimate comments awaiting moderation, and the site's own
 * internal links).
 * Depends on: nothing.
 * Called from: eai-anti-bs-filter.php (cron + activation), detector.php
 * (reads fingerprints), manual-actions.php (trains on manual roast/unroast).
 */
defined('ABSPATH') || exit;

const EAI_FP_OPTION = 'eai_abs_fingerprints_v1';

/**
 * eai_abs_default_keywords
 * Baseline keyword seed list, always merged into trained results so the
 * matcher has a floor even on a brand-new install with no spam history yet.
 * @return string[]
 */
function eai_abs_default_keywords() {
    return [
        'binance', 'crypto', 'usdt', 'telegram', 'whatsapp', 'forex',
        'loan', 'casino', 'betting', 'viagra', 'cialis',
        'gate.io', 'gate.com', 'ref=', 'register?', 'signup',
    ];
}

/**
 * eai_abs_extract_patterns
 * Pull keywords/domains/email-domains out of a single comment's text.
 * Shared by both training (confirmed spam) and manual learning, so there is
 * exactly one place this logic lives.
 * @param  string $content Comment content (lowercased internally).
 * @param  string $url     Author URL (lowercased internally).
 * @param  string $email   Author email (lowercased internally).
 * @return array{keywords: string[], domains: string[], emails: string[]}
 */
function eai_abs_extract_patterns($content, $url = '', $email = '') {
    $content = strtolower(wp_strip_all_tags((string) $content));
    $url     = strtolower((string) $url);
    $email   = strtolower((string) $email);

    $out = ['keywords' => [], 'domains' => [], 'emails' => []];

    // Domains: only pull from the URL field, not freeform sentence text —
    // scanning comment prose for anything-dot-anything catches abbreviations
    // like "e.g." and "i.e." as false "domains".
    if ($url && preg_match_all('/[a-z0-9.\-]{3,}\.[a-z]{2,6}/i', $url, $m)) {
        foreach ($m[0] as $d) {
            $out['domains'][] = strtolower($d);
        }
    }
    // Also pull domains from any links actually present in the content.
    if (preg_match_all('#https?://([a-z0-9.\-]+)#i', $content, $m)) {
        foreach ($m[1] as $d) {
            $out['domains'][] = strtolower($d);
        }
    }

    foreach (eai_abs_default_keywords() as $kw) {
        if ($kw && strpos($content . ' ' . $url, $kw) !== false) {
            $out['keywords'][] = $kw;
        }
    }

    if ($email && strpos($email, '@') !== false) {
        $out['emails'][] = substr($email, strpos($email, '@') + 1);
    }

    return $out;
}

/**
 * eai_abs_train_from_comments
 * Rebuild the fingerprint database from confirmed spam only.
 * Pingbacks/trackbacks are excluded — they are never spam signal.
 * @return array The saved fingerprint set.
 */
function eai_abs_train_from_comments() {
    $patterns = ['keywords' => [], 'domains' => [], 'emails' => []];

    // status=spam ONLY. 'hold' is intentionally excluded — it contains
    // legitimate comments awaiting moderation, not confirmed spam.
    $spam = get_comments([
        'status' => 'spam',
        'number' => 500,
        'type'   => 'comment', // excludes pingback/trackback
    ]);

    foreach ($spam as $c) {
        $found = eai_abs_extract_patterns($c->comment_content, $c->comment_author_url, $c->comment_author_email);
        foreach ($found['keywords'] as $kw) { $patterns['keywords'][$kw] = 1; }
        foreach ($found['domains'] as $d)   { $patterns['domains'][$d] = 1; }
        foreach ($found['emails'] as $e)    { $patterns['emails'][$e] = 1; }
    }

    // Floor of default keywords, always present.
    foreach (eai_abs_default_keywords() as $kw) {
        $patterns['keywords'][$kw] = 1;
    }

    $save = [
        'keywords' => array_keys($patterns['keywords']),
        'domains'  => array_keys($patterns['domains']),
        'emails'   => array_keys($patterns['emails']),
        'ts'       => time(),
    ];

    update_option(EAI_FP_OPTION, $save, false);

    if (EAI_ABS_DEBUG) {
        error_log(sprintf(
            '[EAI] Trained from %d confirmed-spam comments: %d keywords, %d domains, %d email domains',
            count($spam), count($save['keywords']), count($save['domains']), count($save['emails'])
        ));
    }

    return $save;
}

/**
 * eai_abs_add_fingerprint
 * Incrementally add one comment's patterns to the existing fingerprint set,
 * without a full retrain. Used for manual roast (instant learning).
 * @param  array $data Keys: content, url|author_url, email|author_email.
 * @return array The updated fingerprint set.
 */
function eai_abs_add_fingerprint($data) {
    $content = $data['content'] ?? ($data['comment_content'] ?? '');
    $url     = $data['url'] ?? ($data['author_url'] ?? ($data['comment_author_url'] ?? ''));
    $email   = $data['email'] ?? ($data['author_email'] ?? ($data['comment_author_email'] ?? ''));

    if (!$content) {
        return eai_abs_get_fingerprints();
    }

    $fp    = eai_abs_get_fingerprints();
    $found = eai_abs_extract_patterns($content, $url, $email);

    foreach ($found['keywords'] as $kw) {
        if (!in_array($kw, $fp['keywords'], true)) { $fp['keywords'][] = $kw; }
    }
    foreach ($found['domains'] as $d) {
        if (!in_array($d, $fp['domains'], true)) { $fp['domains'][] = $d; }
    }
    foreach ($found['emails'] as $e) {
        if (!in_array($e, $fp['emails'], true)) { $fp['emails'][] = $e; }
    }

    $fp['ts'] = time();
    update_option(EAI_FP_OPTION, $fp, false);

    return $fp;
}

/**
 * eai_abs_get_fingerprints
 * Read the current fingerprint set, training from scratch if none exists yet.
 * @return array
 */
function eai_abs_get_fingerprints() {
    $fp = get_option(EAI_FP_OPTION);
    if (!$fp || !is_array($fp)) {
        $fp = eai_abs_train_from_comments();
    }
    return $fp;
}

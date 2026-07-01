<?php
/**
 * includes/logger.php
 *
 * Writes a JSON audit trail of every sanitize event to logs/spam_log.json.
 * Read-only reference for Jaren — not used for detection logic.
 * Depends on: nothing.
 * Called from: sanitizer.php, manual-actions.php.
 */
defined('ABSPATH') || exit;

/**
 * eai_abs_log_path
 * Resolve (and create if missing) the path to a file inside logs/.
 * @param  string $file Filename, e.g. 'spam_log.json'.
 * @return string Absolute path.
 */
function eai_abs_log_path($file) {
    $base = EAI_ABS_PLUGIN_DIR . 'logs/';
    if (!is_dir($base)) {
        wp_mkdir_p($base);
    }
    return $base . $file;
}

/**
 * eai_abs_log_spam
 * Append one entry to spam_log.json. Always logs full original content —
 * this file is the audit trail, so unlike the live comment it should never
 * be redacted.
 * @param  array  $original  Original comment data (array keys, not WP_Comment).
 * @param  string $reason    e.g. 'auto_sanitized_preinsert', 'manual_roast'.
 * @return void
 */
function eai_abs_log_spam($original, $reason = 'auto_sanitized') {
    $file = eai_abs_log_path('spam_log.json');

    $entry = [
        'ts'      => current_time('mysql'),
        'reason'  => $reason,
        'post_id' => $original['comment_post_ID'] ?? null,
        'orig'    => [
            'author'  => $original['comment_author'] ?? '',
            'email'   => $original['comment_author_email'] ?? '',
            'url'     => $original['comment_author_url'] ?? '',
            'ip'      => $original['comment_author_IP'] ?? '',
            'agent'   => $original['comment_agent'] ?? '',
            'content' => $original['comment_content'] ?? '',
        ],
    ];

    $data = [];
    if (file_exists($file)) {
        $raw  = file_get_contents($file);
        $data = json_decode($raw, true);
        if (!is_array($data)) {
            $data = [];
        }
    }
    $data[] = $entry;

    file_put_contents($file, wp_json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));
}

<?php
defined('ABSPATH') || exit;

function eai_log_path($file) {
    $base = plugin_dir_path(__FILE__) . '../logs/';
    if (!is_dir($base)) { wp_mkdir_p($base); }
    return $base . $file;
}

function eai_log_spam($original, $sanitized, $reason = 'auto_sanitized') {
    $file = eai_log_path('spam_log.json');
    $entry = [
        'ts'        => current_time('mysql'),
        'reason'    => $reason,
        'post_id'   => $sanitized['comment_post_ID'] ?? ($original['comment_post_ID'] ?? null),
        'orig'      => [
            'author'  => $original['comment_author'] ?? '',
            'email'   => $original['comment_author_email'] ?? '',
            'url'     => $original['comment_author_url'] ?? '',
            'ip'      => $original['comment_author_IP'] ?? '',
            'agent'   => $original['comment_agent'] ?? '',
            'content' => $original['comment_content'] ?? '',
        ],
        'sanitized' => [
            'author'  => $sanitized['comment_author'] ?? '',
            'email'   => $sanitized['comment_author_email'] ?? '',
            'content' => $sanitized['comment_content'] ?? '',
        ],
    ];

    $data = [];
    if (file_exists($file)) {
        $raw = file_get_contents($file);
        $data = json_decode($raw, true);
        if (!is_array($data)) $data = [];
    }
    $data[] = $entry;
    file_put_contents($file, wp_json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));
}

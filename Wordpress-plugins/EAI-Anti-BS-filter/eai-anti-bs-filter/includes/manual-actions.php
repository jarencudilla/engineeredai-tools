<?php
/**
 * includes/manual-actions.php
 *
 * Adds manual "🔥 Roast" and "✅ Not Spam" row actions next to WordPress's
 * native Spam/Trash links, for moderator control. Both actions bypass the
 * automatic detector entirely (a human has already made the call) but both
 * feed the fingerprint matcher, so confirmed calls — in either direction —
 * make future auto-detection smarter.
 * "Not Spam" never deletes anything; it just leaves the comment alone and
 * records that this pattern is NOT spam (reserved for future negative-
 * signal use; today it's a no-op restore path plus a training signal).
 * Depends on: sanitizer.php (eai_abs_sanitize_existing_comment is NOT used
 * here on purpose — manual roast skips detection by design), roast-manager.php,
 * fingerprint-matcher.php, logger.php.
 */
defined('ABSPATH') || exit;

/**
 * eai_abs_manual_roast
 * Sanitize a comment immediately, no detector check — the moderator IS the
 * check. Trains the fingerprint matcher from the original content.
 * @param  WP_Comment $comment
 * @return void
 */
function eai_abs_manual_roast($comment) {
    $original = [
        'comment_author'       => $comment->comment_author,
        'comment_author_email' => $comment->comment_author_email,
        'comment_author_url'   => $comment->comment_author_url,
        'comment_content'      => $comment->comment_content,
        'comment_author_IP'    => $comment->comment_author_IP,
        'comment_agent'        => $comment->comment_agent,
        'comment_post_ID'      => $comment->comment_post_ID,
    ];

    update_comment_meta($comment->comment_ID, 'eai_original_spam', wp_json_encode(array_merge(
        $original,
        ['timestamp' => current_time('mysql'), 'manually_flagged' => true]
    )));

    wp_update_comment([
        'comment_ID'           => $comment->comment_ID,
        'comment_content'      => eai_abs_build_roast_content($comment->comment_post_ID),
        'comment_author'       => eai_abs_fake_author(),
        'comment_author_email' => 'sanitized@eai.internal',
        'comment_author_url'   => '',
        'comment_agent'        => trim(($comment->comment_agent ?? '') . ' EAI-SANITIZED'),
    ]);

    wp_set_comment_status($comment->comment_ID, eai_abs_get('auto_approve', true) ? 'approve' : 'hold');
    update_comment_meta($comment->comment_ID, 'eai_sanitized', true);

    eai_abs_add_fingerprint($original);
    eai_abs_log_spam($original, 'manual_roast');
}

/**
 * Row actions: add Roast / Not Spam links to each comment.
 */
add_filter('comment_row_actions', function ($actions, $comment) {
    if (!current_user_can('moderate_comments') || eai_abs_is_pingback_or_trackback($comment)) {
        return $actions;
    }

    $is_roasted = get_comment_meta($comment->comment_ID, 'eai_sanitized', true);
    if ($is_roasted) {
        return $actions; // Already roasted — WP's native Trash/Delete handles cleanup from here.
    }

    $roast_url = wp_nonce_url(
        admin_url("admin-post.php?action=eai_abs_roast&c={$comment->comment_ID}"),
        "eai-abs-roast-{$comment->comment_ID}"
    );
    $notspam_url = wp_nonce_url(
        admin_url("admin-post.php?action=eai_abs_not_spam&c={$comment->comment_ID}"),
        "eai-abs-notspam-{$comment->comment_ID}"
    );

    $actions['eai_abs_roast'] = sprintf(
        '<a href="%s" class="eai-abs-roast" onclick="return confirm(\'Roast this comment and learn from it?\');">🔥 Roast</a>',
        esc_url($roast_url)
    );
    $actions['eai_abs_notspam'] = sprintf(
        '<a href="%s" class="eai-abs-notspam">✅ Not Spam (train)</a>',
        esc_url($notspam_url)
    );

    return $actions;
}, 10, 2);

/**
 * Handler: manual roast action.
 */
add_action('admin_action_eai_abs_roast', function () {
    $comment_id = isset($_GET['c']) ? absint($_GET['c']) : 0;
    if (!$comment_id || !check_admin_referer("eai-abs-roast-{$comment_id}")) {
        wp_die(esc_html__('Invalid request.', 'eai-anti-bs-filter'));
    }
    if (!current_user_can('moderate_comments')) {
        wp_die(esc_html__('Permission denied.', 'eai-anti-bs-filter'));
    }

    $comment = get_comment($comment_id);
    if ($comment) {
        eai_abs_manual_roast($comment);
    }

    wp_safe_redirect(add_query_arg(['eai_abs_roasted' => 1], wp_get_referer() ?: admin_url('edit-comments.php')));
    exit;
});

/**
 * Handler: manual "not spam" action. Does not modify the comment — just
 * records the call as a negative training signal for future use, and
 * leaves WordPress's native comment status untouched.
 */
add_action('admin_action_eai_abs_not_spam', function () {
    $comment_id = isset($_GET['c']) ? absint($_GET['c']) : 0;
    if (!$comment_id || !check_admin_referer("eai-abs-notspam-{$comment_id}")) {
        wp_die(esc_html__('Invalid request.', 'eai-anti-bs-filter'));
    }
    if (!current_user_can('moderate_comments')) {
        wp_die(esc_html__('Permission denied.', 'eai-anti-bs-filter'));
    }

    $comment = get_comment($comment_id);
    if ($comment) {
        update_comment_meta($comment_id, 'eai_confirmed_not_spam', true);
    }

    wp_safe_redirect(add_query_arg(['eai_abs_notspam' => 1], wp_get_referer() ?: admin_url('edit-comments.php')));
    exit;
});

/**
 * Success notices for both actions.
 */
add_action('admin_notices', function () {
    if (isset($_GET['eai_abs_roasted'])) {
        echo '<div class="notice notice-success is-dismissible"><p>🔥 ' .
            esc_html__('Comment roasted and learned from.', 'eai-anti-bs-filter') . '</p></div>';
    }
    if (isset($_GET['eai_abs_notspam'])) {
        echo '<div class="notice notice-success is-dismissible"><p>✅ ' .
            esc_html__('Marked as confirmed not-spam.', 'eai-anti-bs-filter') . '</p></div>';
    }
});

<?php
/**
 * includes/sanitizer.php
 *
 * Wires WordPress comment hooks to detection + sanitization. This file does
 * NOT decide what counts as spam — it calls eai_abs_is_spam() from
 * detector.php for that, every time, before touching a comment. It also
 * hard-skips pingbacks/trackbacks at the top of every hook, so a held or
 * spam-flagged pingback is never mistaken for sanitizable spam.
 * Depends on: detector.php, roast-manager.php, fingerprint-matcher.php,
 * logger.php, settings.php.
 */
defined('ABSPATH') || exit;

/**
 * eai_abs_build_roast_content
 * Compose the replacement comment body shown in place of sanitized spam.
 * @param  int $post_id Unused today, reserved for future per-post roast sets.
 * @return string HTML-safe roast body (line/persona content is plugin-owned,
 *                 not user input).
 */
function eai_abs_build_roast_content($post_id = 0) {
    $phrase = eai_abs_random_phrase();
    $footer = eai_abs_footer_html();
    return "[Filtered by EAI Anti-BS Bot&trade;]\n\n<blockquote>{$phrase}</blockquote>\n\n<small>{$footer}</small>";
}

/**
 * PRE-INSERT: catch and sanitize spam before it ever enters the database.
 */
add_filter('preprocess_comment', function ($commentdata) {
    // Never touch pingbacks/trackbacks, and never touch logged-in moderators.
    if (eai_abs_is_pingback_or_trackback($commentdata) || current_user_can('moderate_comments')) {
        return $commentdata;
    }

    if (!eai_abs_is_spam($commentdata)) {
        return $commentdata;
    }

    $original = $commentdata;

    $commentdata['comment_content']      = eai_abs_build_roast_content($commentdata['comment_post_ID'] ?? 0);
    $commentdata['comment_author']       = eai_abs_fake_author();
    $commentdata['comment_author_email'] = 'sanitized@eai.internal';
    $commentdata['comment_author_url']   = '';
    $commentdata['comment_agent']        = trim(($commentdata['comment_agent'] ?? '') . ' EAI-SANITIZED');

    if (eai_abs_get('auto_approve', true)) {
        $commentdata['comment_approved'] = 1;
    }

    // Save metadata + train once the comment actually has an ID.
    add_action('comment_post', function ($cid) use ($original) {
        add_comment_meta($cid, 'eai_sanitized', true, true);
        add_comment_meta($cid, 'eai_original_spam', wp_json_encode([
            'author'    => $original['comment_author'] ?? '',
            'email'     => $original['comment_author_email'] ?? '',
            'url'       => $original['comment_author_url'] ?? '',
            'content'   => $original['comment_content'] ?? '',
            'ip'        => $original['comment_author_IP'] ?? '',
            'agent'     => $original['comment_agent'] ?? '',
            'timestamp' => current_time('mysql'),
        ]), true);

        eai_abs_log_spam($original, 'auto_sanitized_preinsert');
        eai_abs_add_fingerprint($original);
    }, 10, 1);

    return $commentdata;
}, 9);

/**
 * POST-INSERT: sanitize a comment already in the database (e.g. landed via
 * Akismet or another plugin marking it spam/held after insert).
 * @param  WP_Comment $comment
 * @return void
 */
function eai_abs_sanitize_existing_comment($comment) {
    if (!($comment instanceof WP_Comment) || eai_abs_is_pingback_or_trackback($comment)) {
        return;
    }

    // Already sanitized? Don't double-roast.
    if (get_comment_meta($comment->comment_ID, 'eai_sanitized', true)) {
        return;
    }

    // Re-verify with the detector — WP's own held/spam status is not
    // sufficient grounds on its own.
    if (!eai_abs_is_spam($comment)) {
        return;
    }

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
        ['timestamp' => current_time('mysql')]
    )));

    wp_update_comment([
        'comment_ID'           => $comment->comment_ID,
        'comment_content'      => eai_abs_build_roast_content($comment->comment_post_ID),
        'comment_author'       => eai_abs_fake_author(),
        'comment_author_email' => 'sanitized@eai.internal',
        'comment_author_url'   => '',
        'comment_agent'        => trim(($comment->comment_agent ?? '') . ' EAI-SANITIZED'),
    ]);

    wp_set_comment_status(
        $comment->comment_ID,
        eai_abs_get('auto_approve', true) ? 'approve' : 'hold'
    );

    update_comment_meta($comment->comment_ID, 'eai_sanitized', true);

    eai_abs_add_fingerprint($original);
    eai_abs_log_spam($original, 'post_insert_sanitized');
}

/**
 * Hook: comment transitions TO spam status.
 */
add_action('transition_comment_status', function ($new_status, $old_status, $comment) {
    if ('spam' === $new_status && 'spam' !== $old_status) {
        eai_abs_sanitize_existing_comment($comment);
    }
}, 10, 3);

/**
 * Hook: comment inserted directly as spam or held.
 */
add_action('comment_post', function ($comment_id, $approved) {
    if ($approved === 'spam' || $approved === 0) {
        $comment = get_comment($comment_id);
        if ($comment) {
            eai_abs_sanitize_existing_comment($comment);
        }
    }
}, 99, 2);

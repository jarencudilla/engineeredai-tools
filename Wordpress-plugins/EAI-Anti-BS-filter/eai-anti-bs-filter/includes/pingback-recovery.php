<?php
/**
 * includes/pingback-recovery.php
 *
 * One-off admin tool: restores any comments that were incorrectly sanitized
 * before the detector fix (v1.0.0) — most notably internal pingbacks that
 * earlier versions roasted just for being held by WordPress. Pulled out of
 * manual-actions.php since it's a distinct, one-time-use responsibility.
 * Depends on: nothing beyond WP core comment functions.
 */
defined('ABSPATH') || exit;

add_action('admin_menu', function () {
    add_management_page(
        __('EAI Pingback Recovery', 'eai-anti-bs-filter'),
        __('🔄 Recover Sanitized', 'eai-anti-bs-filter'),
        'manage_options',
        'eai-abs-recover',
        'eai_abs_recovery_page'
    );
});

/**
 * eai_abs_recovery_page
 * Renders the recovery tool screen and handles the restore submit.
 * @return void
 */
function eai_abs_recovery_page() {
    if (!current_user_can('manage_options')) {
        return;
    }
    ?>
    <div class="wrap">
        <h1><?php esc_html_e('Recover Sanitized Comments', 'eai-anti-bs-filter'); ?></h1>
        <p><?php esc_html_e('Restores comments the plugin sanitized in error — useful after upgrading from a version with looser detection (e.g. pingbacks that were wrongly roasted).', 'eai-anti-bs-filter'); ?></p>
        <?php
        if (isset($_POST['eai_abs_recover']) && check_admin_referer('eai_abs_recover_nonce')) {
            $recovered = eai_abs_restore_sanitized();
            printf(
                '<div class="notice notice-success"><p>✅ %s</p></div>',
                esc_html(sprintf(
                    /* translators: %d: number of comments recovered */
                    __('Recovered %d comment(s).', 'eai-anti-bs-filter'),
                    $recovered
                ))
            );
        }
        ?>
        <form method="post">
            <?php wp_nonce_field('eai_abs_recover_nonce'); ?>
            <button type="submit" name="eai_abs_recover" class="button button-primary button-large">
                <?php esc_html_e('Restore Sanitized Comments Now', 'eai-anti-bs-filter'); ?>
            </button>
        </form>
    </div>
    <?php
}

/**
 * eai_abs_restore_sanitized
 * Walks every comment marked eai_sanitized and restores it from its saved
 * eai_original_spam snapshot, then clears the plugin's metadata.
 * @return int Number of comments restored.
 */
function eai_abs_restore_sanitized() {
    $recovered = 0;

    $sanitized = get_comments([
        'meta_key'   => 'eai_sanitized',
        'meta_value' => 1,
        'number'     => 999,
        'type'       => 'all',
    ]);

    foreach ($sanitized as $comment) {
        $original_json = get_comment_meta($comment->comment_ID, 'eai_original_spam', true);
        if (!$original_json) {
            continue;
        }

        $original = json_decode($original_json, true);
        if (!$original) {
            continue;
        }

        wp_update_comment([
            'comment_ID'           => $comment->comment_ID,
            'comment_author'       => $original['comment_author'] ?? $original['author'] ?? $comment->comment_author,
            'comment_author_email' => $original['comment_author_email'] ?? $original['email'] ?? $comment->comment_author_email,
            'comment_author_url'   => $original['comment_author_url'] ?? $original['url'] ?? $comment->comment_author_url,
            'comment_content'      => $original['comment_content'] ?? $original['content'] ?? $comment->comment_content,
            'comment_agent'        => str_replace(' EAI-SANITIZED', '', $original['comment_agent'] ?? $original['agent'] ?? $comment->comment_agent),
        ]);

        delete_comment_meta($comment->comment_ID, 'eai_sanitized');
        delete_comment_meta($comment->comment_ID, 'eai_original_spam');

        $recovered++;
    }

    return $recovered;
}

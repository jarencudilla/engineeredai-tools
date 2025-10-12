<?php
defined('ABSPATH') || exit;

/**
 * Add "🔥 Roast This" button to every comment in admin
 */
add_filter('comment_row_actions', function ($actions, $comment) {
    if (current_user_can('moderate_comments')) {
        $nonce_url = wp_nonce_url(
            admin_url("comment.php?c={$comment->comment_ID}&action=eai_roast_spam"),
            "eai-roast-{$comment->comment_ID}"
        );
        
        // Check if already roasted
        $is_roasted = get_comment_meta($comment->comment_ID, 'eai_sanitized', true);
        
        if ($is_roasted) {
            // Show "View Original" for roasted comments
            $actions['eai_view_original'] = sprintf(
                '<a href="#" class="eai-view-original" data-comment-id="%d">👀 View Original Spam</a>',
                $comment->comment_ID
            );
        } else {
            // Show "Roast" button for non-roasted comments
            $actions['eai_roast'] = sprintf(
                '<a href="%s" class="eai-roast-comment" onclick="return confirm(\'Roast this spam and learn from it?\');">🔥 Roast This</a>',
                $nonce_url
            );
        }
    }
    return $actions;
}, 10, 2);

/**
 * Handle manual roast action
 */
add_action('admin_action_eai_roast_spam', function () {
    $comment_id = isset($_GET['c']) ? absint($_GET['c']) : 0;
    
    if (!$comment_id || !check_admin_referer("eai-roast-{$comment_id}")) {
        wp_die('Invalid request');
    }

    if (!current_user_can('moderate_comments')) {
        wp_die('Permission denied');
    }

    $comment = get_comment($comment_id);
    if (!$comment) {
        wp_die('Comment not found');
    }

    // Save original data BEFORE sanitizing
    $original = [
        'author' => $comment->comment_author,
        'email' => $comment->comment_author_email,
        'url' => $comment->comment_author_url,
        'content' => $comment->comment_content,
        'ip' => $comment->comment_author_IP,
        'user_agent' => $comment->comment_agent,
        'timestamp' => current_time('mysql'),
        'manually_flagged' => true
    ];

    // Train from this spam (CRITICAL: This is how it learns!)
    if (function_exists('eai_add_spam_fingerprint')) {
        eai_add_spam_fingerprint($original);
        error_log('[EAI] 📚 Learned from manual roast: ' . $comment->comment_author);
    }

    // Log to spam database
    if (function_exists('eai_log_spam')) {
        eai_log_spam($original, [], 'manual_roast');
    }

    // Now sanitize it
    eai_sanitize_existing_comment($comment);

    // Redirect back with success message
    wp_redirect(add_query_arg([
        'roasted' => 1,
        'learned' => 1
    ], admin_url('edit-comments.php')));
    exit;
});

/**
 * Bulk action: Roast multiple comments at once
 */
add_filter('bulk_actions-edit-comments', function ($actions) {
    $actions['eai_bulk_roast'] = '🔥 Roast Selected Comments';
    return $actions;
});

add_filter('handle_bulk_actions-edit-comments', function ($redirect, $action, $comment_ids) {
    if ($action !== 'eai_bulk_roast') {
        return $redirect;
    }

    $roasted = 0;
    foreach ($comment_ids as $comment_id) {
        $comment = get_comment($comment_id);
        if (!$comment) continue;

        // Save and learn from original
        $original = [
            'author' => $comment->comment_author,
            'email' => $comment->comment_author_email,
            'url' => $comment->comment_author_url,
            'content' => $comment->comment_content,
            'ip' => $comment->comment_author_IP,
            'user_agent' => $comment->comment_agent,
            'timestamp' => current_time('mysql'),
            'manually_flagged' => true
        ];

        if (function_exists('eai_add_spam_fingerprint')) {
            eai_add_spam_fingerprint($original);
        }

        eai_sanitize_existing_comment($comment);
        $roasted++;
    }

    return add_query_arg([
        'roasted' => $roasted,
        'learned' => $roasted
    ], $redirect);
}, 10, 3);

/**
 * Show success notices
 */
add_action('admin_notices', function () {
    if (isset($_GET['roasted']) && isset($_GET['learned'])) {
        $count = absint($_GET['roasted']);
        printf(
            '<div class="notice notice-success is-dismissible"><p>🔥 <strong>%d comment%s roasted</strong> and learned from! The plugin is now smarter.</p></div>',
            $count,
            $count === 1 ? '' : 's'
        );
    }
});

/**
 * AJAX: View original spam content
 */
add_action('wp_ajax_eai_view_original_spam', function () {
    check_ajax_referer('eai-view-original', 'nonce');
    
    $comment_id = isset($_POST['comment_id']) ? absint($_POST['comment_id']) : 0;
    if (!$comment_id || !current_user_can('moderate_comments')) {
        wp_send_json_error('Permission denied');
    }

    $original = get_comment_meta($comment_id, 'eai_original_spam', true);
    if (!$original) {
        wp_send_json_error('No original spam data found');
    }

    $data = json_decode($original, true);
    wp_send_json_success([
        'author' => $data['author'] ?? 'Unknown',
        'email' => $data['email'] ?? 'Unknown',
        'url' => $data['url'] ?? '',
        'content' => $data['content'] ?? '',
        'timestamp' => $data['timestamp'] ?? 'Unknown'
    ]);
});

/**
 * Add JavaScript for "View Original" modal
 */
add_action('admin_footer-edit-comments.php', function () {
    ?>
    <script>
    jQuery(document).ready(function($) {
        // View original spam modal
        $(document).on('click', '.eai-view-original', function(e) {
            e.preventDefault();
            var commentId = $(this).data('comment-id');
            
            $.post(ajaxurl, {
                action: 'eai_view_original_spam',
                nonce: '<?php echo wp_create_nonce('eai-view-original'); ?>',
                comment_id: commentId
            }, function(response) {
                if (response.success) {
                    var d = response.data;
                    var html = '<div style="background: #fff; padding: 20px; border-radius: 5px; max-width: 600px;">' +
                        '<h2>🗑️ Original Spam Content</h2>' +
                        '<p><strong>Author:</strong> ' + d.author + '</p>' +
                        '<p><strong>Email:</strong> ' + d.email + '</p>' +
                        '<p><strong>URL:</strong> ' + (d.url || '(none)') + '</p>' +
                        '<p><strong>Time:</strong> ' + d.timestamp + '</p>' +
                        '<p><strong>Content:</strong></p>' +
                        '<blockquote style="background: #f5f5f5; padding: 15px; border-left: 4px solid #dc3545;">' + 
                        d.content + '</blockquote>' +
                        '<button onclick="this.closest(\'div\').remove();" style="margin-top: 15px;">Close</button>' +
                        '</div>';
                    
                    $('body').append('<div class="eai-modal-overlay" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7); z-index: 999999; display: flex; align-items: center; justify-content: center;" onclick="this.remove()">' + html + '</div>');
                } else {
                    alert('Could not load original spam data');
                }
            });
        });
    });
    </script>
    <style>
    .eai-roast-comment { color: #dc3545 !important; font-weight: bold; }
    .eai-view-original { color: #6c757d !important; }
    </style>
    <?php
});

/**
 * === PINGBACK RECOVERY ===
 * Add this to the bottom of manual-actions.php
 */

add_action('admin_menu', function() {
    add_management_page(
        'EAI Pingback Recovery',
        '🔄 Recover Pingbacks',
        'manage_options',
        'eai-recover-pingbacks',
        'eai_pingback_recovery_page'
    );
});

function eai_pingback_recovery_page() {
    ?>
    <div class="wrap">
        <h1>🔄 Recover Sanitized Pingbacks</h1>
        <p>This will restore all legitimate pingbacks that were accidentally sanitized.</p>
        
        <?php
        if (isset($_POST['eai_recover_pingbacks']) && check_admin_referer('eai_recover_nonce')) {
            $recovered = eai_restore_pingbacks();
            echo '<div class="notice notice-success"><p>✅ Recovered ' . $recovered . ' pingbacks!</p></div>';
        }
        ?>
        
        <form method="post">
            <?php wp_nonce_field('eai_recover_nonce'); ?>
            <button type="submit" name="eai_recover_pingbacks" class="button button-primary button-large">
                🔧 Restore Pingbacks Now
            </button>
        </form>
    </div>
    <?php
}

function eai_restore_pingbacks() {
    $recovered = 0;
    
    // Get all comments with eai_sanitized metadata
    $args = [
        'meta_key' => 'eai_sanitized',
        'meta_value' => 1,
        'number' => 999,
        'type' => 'all'
    ];
    
    $sanitized = get_comments($args);

    foreach ($sanitized as $comment) {
        // Get original data
        $original_json = get_comment_meta($comment->comment_ID, 'eai_original_spam', true);
        if (!$original_json) continue;

        $original = json_decode($original_json, true);
        if (!$original) continue;

        // Restore the comment
        wp_update_comment([
            'comment_ID' => $comment->comment_ID,
            'comment_author' => $original['author'] ?? $comment->comment_author,
            'comment_author_email' => $original['email'] ?? $comment->comment_author_email,
            'comment_author_url' => $original['url'] ?? $comment->comment_author_url,
            'comment_content' => $original['content'] ?? $comment->comment_content,
            'comment_agent' => str_replace(' EAI-SANITIZED', '', $original['agent'] ?? $comment->comment_agent),
        ]);

        // Remove EAI metadata
        delete_comment_meta($comment->comment_ID, 'eai_sanitized');
        delete_comment_meta($comment->comment_ID, 'eai_original_spam');

        $recovered++;
        error_log('[EAI] ✅ Recovered comment_id=' . $comment->comment_ID);
    }

    return $recovered;
}
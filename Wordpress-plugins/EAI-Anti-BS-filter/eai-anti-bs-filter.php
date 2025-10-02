<?php
/**
 * Plugin Name: EAI Anti-BS Filter
 * Description: Spam comment sanitizer that learns from your blog's flagged spam. Roasts instead of deletes. Lite version includes forced EAI linkback.
 * Version: 0.3.0
 * Author: EngineeredAI
 */

defined('ABSPATH') || exit;

// Toggle hard “Pro” (no linkback). You can also enable Pro in the Settings page.
if (!defined('EAI_ANTI_BS_PRO')) {
    define('EAI_ANTI_BS_PRO', false);
}

/**
 * Bootstrap includes (order matters).
 */
try {
    require_once plugin_dir_path(__FILE__) . 'includes/logger.php';
require_once plugin_dir_path(__FILE__) . 'includes/settings.php';        // MUST load before roast/dashboard/sanitizer
require_once plugin_dir_path(__FILE__) . 'includes/roast-manager.php';
require_once plugin_dir_path(__FILE__) . 'includes/fingerprint-matcher.php';
require_once plugin_dir_path(__FILE__) . 'includes/sanitizer.php';
require_once plugin_dir_path(__FILE__) . 'includes/manual-actions.php';
require_once plugin_dir_path(__FILE__) . 'includes/dashboard.php';

} catch (Throwable $e) {
    error_log('EAI Anti-BS Filter include error: ' . $e->getMessage());
}

error_log('✅ EAI Anti-BS Filter v0.3.0 loaded');

/**
 * Activation / Deactivation
 */
register_activation_hook(__FILE__, function () {
    // Schedule hourly retraining if not scheduled.
    if (!wp_next_scheduled('eai_elearn_cron')) {
        wp_schedule_event(time() + 60, 'hourly', 'eai_elearn_cron');
    }

    // Seed fingerprints from existing spam/mod queue on first install/activate.
    if (function_exists('eai_train_from_comments')) {
        eai_train_from_comments();
    }
});

register_deactivation_hook(__FILE__, function () {
    // Clear our cron
    wp_clear_scheduled_hook('eai_elearn_cron');
});

/**
 * Cron: periodic re-training from spam + moderation queue.
 */
add_action('eai_elearn_cron', function () {
    if (function_exists('eai_train_from_comments')) {
        eai_train_from_comments();
    }
});

/**
 * If Akismet/core marks a comment as spam after insert,
 * convert it into a roast and (optionally) auto-approve based on settings.
 */
add_action('transition_comment_status', function ($new, $old, $comment) {
    if ('spam' === $new && function_exists('eai_sanitize_existing_comment')) {
        eai_sanitize_existing_comment($comment);
    }
}, 10, 3);

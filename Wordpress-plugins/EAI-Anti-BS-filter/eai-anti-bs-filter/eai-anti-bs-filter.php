<?php
/**
 * Plugin Name: EAI Anti-BS Filter
 * Plugin URI:  https://engineeredai.net
 * Description: Sanitizes spam comments instead of deleting them — replaces name, email, and content with a roast, then learns from confirmed spam to improve detection over time. Lite version includes an EAI linkback in the roast footer.
 * Version:     1.0.0
 * Author:      EngineeredAI
 * Author URI:  https://engineeredai.net
 * License:     GPLv2 or later
 * License URI: https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain: eai-anti-bs-filter
 *
 * What this file does:
 * Bootstraps the plugin — loads all includes in dependency order, registers
 * activation/deactivation hooks (cron scheduling + initial fingerprint seed).
 *
 * Load order matters:
 * settings -> logger -> fingerprint-matcher -> detector -> sanitizer ->
 * roast-manager -> manual-actions -> dashboard
 * (settings/logger/fingerprint-matcher must load before anything that reads
 * options or trains from them; detector must load before sanitizer, which
 * calls it.)
 */
defined('ABSPATH') || exit;

// Toggle hard "Pro" (no linkback). Can also be set via the Settings page.
if (!defined('EAI_ANTI_BS_PRO')) {
    define('EAI_ANTI_BS_PRO', false);
}

// Debug logging — OFF by default for a public release. Define true in
// wp-config.php for troubleshooting: define('EAI_ABS_DEBUG', true);
if (!defined('EAI_ABS_DEBUG')) {
    define('EAI_ABS_DEBUG', false);
}

define('EAI_ABS_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('EAI_ABS_PLUGIN_FILE', __FILE__);

/**
 * Bootstrap includes (order matters — see file header).
 */
try {
    require_once EAI_ABS_PLUGIN_DIR . 'includes/settings.php';
    require_once EAI_ABS_PLUGIN_DIR . 'includes/logger.php';
    require_once EAI_ABS_PLUGIN_DIR . 'includes/fingerprint-matcher.php';
    require_once EAI_ABS_PLUGIN_DIR . 'includes/detector.php';
    require_once EAI_ABS_PLUGIN_DIR . 'includes/roast-manager.php';
    require_once EAI_ABS_PLUGIN_DIR . 'includes/sanitizer.php';
    require_once EAI_ABS_PLUGIN_DIR . 'includes/manual-actions.php';
    require_once EAI_ABS_PLUGIN_DIR . 'includes/pingback-recovery.php';
    require_once EAI_ABS_PLUGIN_DIR . 'includes/dashboard.php';
} catch (Throwable $e) {
    error_log('EAI Anti-BS Filter include error: ' . $e->getMessage());
}

/**
 * Activation / Deactivation
 */
register_activation_hook(__FILE__, function () {
    // Schedule hourly retraining if not already scheduled.
    if (!wp_next_scheduled('eai_abs_retrain_cron')) {
        wp_schedule_event(time() + 60, 'hourly', 'eai_abs_retrain_cron');
    }
    // Seed fingerprints from existing confirmed spam on first install/activate.
    if (function_exists('eai_abs_train_from_comments')) {
        eai_abs_train_from_comments();
    }
});

register_deactivation_hook(__FILE__, function () {
    wp_clear_scheduled_hook('eai_abs_retrain_cron');
});

// Hourly retrain hook target.
add_action('eai_abs_retrain_cron', function () {
    if (function_exists('eai_abs_train_from_comments')) {
        eai_abs_train_from_comments();
    }
});

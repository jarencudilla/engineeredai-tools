<?php
/**
 * includes/settings.php
 *
 * Single source of truth for plugin settings (stored as one wp_options row).
 * What it connects to: dashboard.php (reads/writes via the Settings API),
 * roast-manager.php, detector.php, sanitizer.php (read via eai_abs_get()).
 * Depends on: nothing — must load first.
 */
defined('ABSPATH') || exit;

const EAI_ABS_OPTION = 'eai_abs_settings';

/**
 * eai_abs_default_settings
 * The full default shape of the settings array. Anything missing from a
 * saved option gets backfilled with these on read, so older saved options
 * never produce undefined-index warnings as new settings are added.
 * @return array
 */
function eai_abs_default_settings() {
    return [
        'auto_approve' => true,
        'pro_mode'     => false,
        'personas'     => [],
        'lines'        => [],
    ];
}

/**
 * eai_abs_get_settings
 * Fetch the full settings array, merged with defaults.
 * @return array
 */
function eai_abs_get_settings() {
    $s = get_option(EAI_ABS_OPTION);
    if (!is_array($s)) {
        $s = [];
    }
    return array_merge(eai_abs_default_settings(), $s);
}

/**
 * eai_abs_update_settings
 * Merge and persist new settings on top of current ones.
 * @param  array $new Partial or full settings to merge in.
 * @return array The merged settings actually saved.
 */
function eai_abs_update_settings($new) {
    $current = eai_abs_get_settings();
    $merged  = array_merge($current, is_array($new) ? $new : []);
    update_option(EAI_ABS_OPTION, $merged, false);
    return $merged;
}

/**
 * eai_abs_get
 * Convenience getter for a single settings key.
 * @param  string $key
 * @param  mixed  $fallback
 * @return mixed
 */
function eai_abs_get($key, $fallback = null) {
    $s = eai_abs_get_settings();
    return array_key_exists($key, $s) ? $s[$key] : $fallback;
}

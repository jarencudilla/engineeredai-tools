<?php
defined('ABSPATH') || exit;

const EAI_ABS_OPTION = 'eai_abs_settings';

function eai_abs_default_settings() {
    return [
        'auto_approve' => true,
        'pro_mode'     => false,
        'personas'     => [],
        'lines'        => [],
    ];
}

function eai_abs_get_settings() {
    $s = get_option(EAI_ABS_OPTION);
    if (!is_array($s)) $s = [];
    return array_merge(eai_abs_default_settings(), $s);
}

function eai_abs_update_settings($new) {
    $current = eai_abs_get_settings();
    $merged  = array_merge($current, is_array($new) ? $new : []);
    update_option(EAI_ABS_OPTION, $merged, false);
    return $merged;
}

function eai_abs_get($key, $fallback = null) {
    $s = eai_abs_get_settings();
    return array_key_exists($key, $s) ? $s[$key] : $fallback;
}

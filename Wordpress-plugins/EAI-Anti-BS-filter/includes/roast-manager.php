<?php
defined('ABSPATH') || exit;

function eai_get_random_phrase($post_id = 0) {
    $settings_lines = eai_abs_get('lines', []);
    if (is_array($settings_lines) && count($settings_lines) > 0) {
        return $settings_lines[array_rand($settings_lines)];
    }
    $path = plugin_dir_path(__FILE__) . '../logs/roast_lines.json';
    if (!file_exists($path)) return "This was spam. It got rebooted.";
    $phrases = json_decode(file_get_contents($path), true);
    if (!is_array($phrases) || empty($phrases)) return "This was spam. It got rebooted.";
    return $phrases[array_rand($phrases)];
}

function eai_get_fake_author() {
    $settings_personas = eai_abs_get('personas', []);
    if (is_array($settings_personas) && count($settings_personas) > 0) {
        return $settings_personas[array_rand($settings_personas)];
    }
    $path = plugin_dir_path(__FILE__) . '../logs/roast_personas.json';
    if (!file_exists($path)) return "Anonymous Roasted";
    $names = json_decode(file_get_contents($path), true);
    if (!is_array($names) || empty($names)) return "Anonymous Roasted";
    return $names[array_rand($names)];
}

function eai_roast_footer_html() {
    $pro_setting = eai_abs_get('pro_mode', false);
    $pro_const   = (defined('EAI_ANTI_BS_PRO') && EAI_ANTI_BS_PRO);
    $site_url    = get_site_url();
    $is_eai      = stripos($site_url, 'engineeredai.net') !== false;

    if ($is_eai || $pro_setting || $pro_const) {
        return 'Sanitized by EAI Anti-BS Bot™';
    }
    return '<a href="https://engineeredai.net" rel="noopener nofollow" target="_blank">Sanitized by EAI Anti-BS Bot™</a>';
}

<?php
/**
 * includes/roast-manager.php
 *
 * Picks a random roast line + fake persona for sanitized comments, and
 * builds the linkback footer (Lite shows a linked credit; Pro/EAI-owned
 * sites show plain text, no link).
 * Depends on: settings.php (eai_abs_get).
 * Called from: sanitizer.php, manual-actions.php.
 */
defined('ABSPATH') || exit;

/**
 * eai_abs_random_phrase
 * @return string A roast line — from saved settings if present, otherwise
 *                falls back to the bundled defaults JSON.
 */
function eai_abs_random_phrase() {
    $lines = eai_abs_get('lines', []);
    if (is_array($lines) && count($lines) > 0) {
        return $lines[array_rand($lines)];
    }
    $path = EAI_ABS_PLUGIN_DIR . 'logs/roast_lines.json';
    if (!file_exists($path)) {
        return 'This was spam. It got rebooted.';
    }
    $phrases = json_decode(file_get_contents($path), true);
    if (!is_array($phrases) || empty($phrases)) {
        return 'This was spam. It got rebooted.';
    }
    return $phrases[array_rand($phrases)];
}

/**
 * eai_abs_fake_author
 * @return string A roast persona name, same fallback pattern as above.
 */
function eai_abs_fake_author() {
    $personas = eai_abs_get('personas', []);
    if (is_array($personas) && count($personas) > 0) {
        return $personas[array_rand($personas)];
    }
    $path = EAI_ABS_PLUGIN_DIR . 'logs/roast_personas.json';
    if (!file_exists($path)) {
        return 'Anonymous Roasted';
    }
    $names = json_decode(file_get_contents($path), true);
    if (!is_array($names) || empty($names)) {
        return 'Anonymous Roasted';
    }
    return $names[array_rand($names)];
}

/**
 * eai_abs_footer_html
 * Lite version links back to engineeredai.net. Pro mode (set via settings
 * or the EAI_ANTI_BS_PRO constant) drops the link. EAI's own site never
 * shows the link to itself either way.
 * @return string Footer HTML, safe to echo directly (no user input).
 */
function eai_abs_footer_html() {
    $pro_setting = eai_abs_get('pro_mode', false);
    $pro_const   = (defined('EAI_ANTI_BS_PRO') && EAI_ANTI_BS_PRO);
    $is_eai_site = stripos(get_site_url(), 'engineeredai.net') !== false;

    if ($is_eai_site || $pro_setting || $pro_const) {
        return 'Sanitized by EAI Anti-BS Bot&trade;';
    }
    return '<a href="https://engineeredai.net" rel="noopener nofollow" target="_blank">Sanitized by EAI Anti-BS Bot&trade;</a>';
}

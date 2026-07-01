<?php
/**
 * title-stack.php
 *
 * Resolves the best card title for a given post ID.
 * Priority: custom field → SEO plugin title → AI generated → post title.
 * AI generation only fires if provider + key are configured in settings.
 *
 * @package RelayCard
 */

if ( ! defined( 'ABSPATH' ) ) exit;

/**
 * relaycard_get_card_title
 * Returns the best available title for a post card.
 *
 * @param  int     $post_id   Post ID to resolve title for.
 * @param  string  $fallback  Raw post title as last resort.
 * @return string
 */
function relaycard_get_card_title( $post_id, $fallback ) {

    // 1. Manual override via custom field — highest priority
    $custom = get_post_meta( $post_id, 'card_title', true );
    if ( ! empty( $custom ) ) return $custom;

    // 2. SEO plugin title — RankMath → Yoast → AIOSEO
    $seo_title = relaycard_get_seo_title( $post_id );
    if ( ! empty( $seo_title ) ) return $seo_title;

    // 3. AI generated hook title — only if provider + key set
    $ai_title = relaycard_get_ai_title( $fallback );
    if ( ! empty( $ai_title ) ) return $ai_title;

    // 4. Post title — always available
    return $fallback;
}

/**
 * relaycard_get_seo_title
 * Checks for RankMath, Yoast, AIOSEO meta title in that order.
 *
 * @param  int     $post_id
 * @return string|null
 */
function relaycard_get_seo_title( $post_id ) {
    // RankMath
    $rm = get_post_meta( $post_id, 'rank_math_title', true );
    if ( ! empty( $rm ) ) return $rm;

    // Yoast
    $yoast = get_post_meta( $post_id, '_yoast_wpseo_title', true );
    if ( ! empty( $yoast ) ) return $yoast;

    // AIOSEO
    $aio = get_post_meta( $post_id, '_aioseo_title', true );
    if ( ! empty( $aio ) ) return $aio;

    return null;
}

/**
 * relaycard_get_ai_title
 * Calls configured AI provider to generate a hook title from post title.
 * Returns null if no provider/key configured or if API call fails.
 *
 * @param  string  $post_title   Raw post title to rewrite.
 * @return string|null
 */
function relaycard_get_ai_title( $post_title ) {
    $options  = get_option( 'relaycard_settings', [] );
    $provider = $options['ai_provider'] ?? '';
    $key      = $options['ai_key'] ?? '';

    if ( empty( $provider ) || empty( $key ) ) return null;

    $prompt = "Rewrite this blog post title as a short, punchy hook title for an inline promotional card. Max 10 words. Hook-first. No generic words like 'guide' or 'tips'. Make it create curiosity or tension. Return only the title, nothing else.\n\nTitle: {$post_title}";

    switch ( $provider ) {
        case 'gemini':
            return relaycard_call_gemini( $key, $prompt );
        case 'openai':
            return relaycard_call_openai( $key, $prompt );
        case 'claude':
            return relaycard_call_claude( $key, $prompt );
        default:
            return null;
    }
}

/**
 * relaycard_call_gemini
 */
function relaycard_call_gemini( $key, $prompt ) {
    $url      = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={$key}";
    $response = wp_remote_post( $url, [
        'timeout' => 8,
        'headers' => [ 'Content-Type' => 'application/json' ],
        'body'    => json_encode( [
            'contents' => [ [ 'parts' => [ [ 'text' => $prompt ] ] ] ]
        ] ),
    ] );
    if ( is_wp_error( $response ) ) return null;
    $body = json_decode( wp_remote_retrieve_body( $response ), true );
    return $body['candidates'][0]['content']['parts'][0]['text'] ?? null;
}

/**
 * relaycard_call_openai
 */
function relaycard_call_openai( $key, $prompt ) {
    $response = wp_remote_post( 'https://api.openai.com/v1/chat/completions', [
        'timeout' => 8,
        'headers' => [
            'Content-Type'  => 'application/json',
            'Authorization' => "Bearer {$key}",
        ],
        'body' => json_encode( [
            'model'    => 'gpt-4o-mini',
            'messages' => [ [ 'role' => 'user', 'content' => $prompt ] ],
            'max_tokens' => 30,
        ] ),
    ] );
    if ( is_wp_error( $response ) ) return null;
    $body = json_decode( wp_remote_retrieve_body( $response ), true );
    return $body['choices'][0]['message']['content'] ?? null;
}

/**
 * relaycard_call_claude
 */
function relaycard_call_claude( $key, $prompt ) {
    $response = wp_remote_post( 'https://api.anthropic.com/v1/messages', [
        'timeout' => 8,
        'headers' => [
            'Content-Type'      => 'application/json',
            'x-api-key'         => $key,
            'anthropic-version' => '2023-06-01',
        ],
        'body' => json_encode( [
            'model'      => 'claude-haiku-4-5-20251001',
            'max_tokens' => 30,
            'messages'   => [ [ 'role' => 'user', 'content' => $prompt ] ],
        ] ),
    ] );
    if ( is_wp_error( $response ) ) return null;
    $body = json_decode( wp_remote_retrieve_body( $response ), true );
    return $body['content'][0]['text'] ?? null;
}

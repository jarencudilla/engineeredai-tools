<?php
/**
 * card-engine.php
 *
 * Core card builder and content injection filter.
 * Counts headings, determines card slots, builds card HTML, injects before trigger headings.
 * Reads settings from relaycard_settings option.
 *
 * @package RelayCard
 */

if ( ! defined( 'ABSPATH' ) ) exit;

// — Hook into post content —
add_filter( 'the_content', 'relaycard_inject_cards' );

/**
 * relaycard_inject_cards
 * Main filter. Counts headings, fetches related posts, builds and injects cards.
 *
 * @param  string  $content  Raw post content HTML.
 * @return string            Content with cards injected.
 */
function relaycard_inject_cards( $content ) {
    if ( ! is_single() || ! in_the_loop() || ! is_main_query() ) return $content;

    $options = get_option( 'relaycard_settings', [] );

    // — Count all H2/H3/H4 headings —
    preg_match_all( '/<h[2-4][\s>]/i', $content, $matches );
    $total = count( $matches[0] );

    // — Need at least 4 headings for any card to fire cleanly —
    if ( $total < 4 ) return $content;

    // — Determine card count and injection points —
    $max_cards   = $total >= 6 ? 2 : 1;
    $trigger_map = $max_cards === 2
        ? [ 3, 5 ]
        : [ (int) ceil( $total / 2 ) ];

    // — Fetch related posts —
    $post_id = get_the_ID();
    $posts   = relaycard_get_related_posts( $post_id, $max_cards );
    if ( empty( $posts ) ) return $content;

    // — Build card HTML for each related post —
    $cards = [];
    foreach ( $posts as $related ) {
        $title   = relaycard_get_card_title( $related['id'], $related['title'] );
        $cards[] = relaycard_build_card( $related['thumb'], $title, $related['link'], $options );
    }

    if ( empty( $cards ) ) return $content;

    // — Split content at each heading, inject card BEFORE trigger heading —
    $parts      = preg_split( '/(?=<h[2-4][\s>])/i', $content );
    $output     = '';
    $head_count = 0;
    $card_index = 0;

    foreach ( $parts as $part ) {
        if ( preg_match( '/<h[2-4][\s>]/i', $part ) ) {
            $head_count++;
            // Inject before this heading if it's a trigger point
            if ( in_array( $head_count, $trigger_map ) && isset( $cards[ $card_index ] ) ) {
                $output .= $cards[ $card_index ];
                $card_index++;
            }
        }
        $output .= $part;
    }

    return $output;
}

/**
 * relaycard_build_card
 * Builds card HTML based on selected style from settings.
 *
 * @param  string  $thumb    Featured image URL.
 * @param  string  $title    Card title (already resolved via title stack).
 * @param  string  $link     Post permalink.
 * @param  array   $options  Plugin settings array.
 * @return string            Card HTML.
 */
function relaycard_build_card( $thumb, $title, $link, $options ) {
    $style     = $options['card_style']  ?? 'split';
    $cta       = $options['cta_text']    ?? 'Read More &rarr;';
    $label     = $options['card_label']  ?? '';
    $font      = $options['font_cat']    ?? 'sans';
    $ratio     = $options['img_ratio']   ?? '60'; // 50, 60, 70
    $accent    = $options['accent']      ?? '#e05a2b';

    $font_class   = 'relaycard-font-' . esc_attr( $font );
    $ratio_class  = 'relaycard-ratio-' . esc_attr( $ratio );
    $style_class  = 'relaycard-style-' . esc_attr( $style );
    $label_html   = $label ? '<span class="relaycard-label">' . esc_html( $label ) . '</span>' : '';
    $accent_style = 'style="--rc-accent:' . esc_attr( $accent ) . ';"';

    $attribution = relaycard_attribution();

    if ( $style === 'overlay' ) {
        return '
        <div class="relaycard ' . $style_class . ' ' . $font_class . '" ' . $accent_style . '>
            <a class="relaycard-link" href="' . esc_url( $link ) . '">
                <div class="relaycard-img" style="background-image:url(' . esc_url( $thumb ) . ');">
                    ' . $label_html . '
                    <div class="relaycard-overlay-body">
                        <div class="relaycard-title">' . esc_html( $title ) . '</div>
                        <span class="relaycard-cta">' . wp_kses_post( $cta ) . '</span>
                    </div>
                </div>
            </a>
            ' . $attribution . '
        </div>';
    }

    if ( $style === 'cinematic' ) {
        return '
        <div class="relaycard ' . $style_class . ' ' . $font_class . '" ' . $accent_style . '>
            <a class="relaycard-link" href="' . esc_url( $link ) . '">
                <div class="relaycard-img relaycard-img--cinematic" style="background-image:url(' . esc_url( $thumb ) . ');">
                    ' . $label_html . '
                    <div class="relaycard-cinematic-body">
                        <div class="relaycard-title">' . esc_html( $title ) . '</div>
                        <span class="relaycard-cta">' . wp_kses_post( $cta ) . '</span>
                    </div>
                </div>
            </a>
            ' . $attribution . '
        </div>';
    }

    if ( $style === 'minimal' ) {
        return '
        <div class="relaycard ' . $style_class . ' ' . $font_class . '" ' . $accent_style . '>
            <a class="relaycard-link relaycard-minimal-inner" href="' . esc_url( $link ) . '">
                ' . $label_html . '
                <div class="relaycard-title">' . esc_html( $title ) . '</div>
                <span class="relaycard-cta">' . wp_kses_post( $cta ) . '</span>
            </a>
            ' . $attribution . '
        </div>';
    }

    if ( $style === 'story' ) {
        return '
        <div class="relaycard ' . $style_class . ' ' . $font_class . '" ' . $accent_style . '>
            <a class="relaycard-link" href="' . esc_url( $link ) . '">
                <div class="relaycard-img relaycard-img--story" style="background-image:url(' . esc_url( $thumb ) . ');"></div>
                <div class="relaycard-story-body">
                    ' . $label_html . '
                    <div class="relaycard-title">' . esc_html( $title ) . '</div>
                    <span class="relaycard-cta">' . wp_kses_post( $cta ) . '</span>
                </div>
            </a>
            ' . $attribution . '
        </div>';
    }

    // Default: split
    return '
    <div class="relaycard relaycard-style-split ' . $ratio_class . ' ' . $font_class . '" ' . $accent_style . '>
        <a class="relaycard-link relaycard-split-inner" href="' . esc_url( $link ) . '">
            <div class="relaycard-img" style="background-image:url(' . esc_url( $thumb ) . ');"></div>
            <div class="relaycard-split-body">
                ' . $label_html . '
                <div class="relaycard-title">' . esc_html( $title ) . '</div>
                <span class="relaycard-cta">' . wp_kses_post( $cta ) . '</span>
            </div>
        </a>
        ' . $attribution . '
    </div>';
}

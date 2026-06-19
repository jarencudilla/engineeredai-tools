<?php
/**
 * preview-ajax.php
 *
 * AJAX handler for live card preview in admin.
 * Builds a sample card using current settings and returns HTML.
 *
 * @package RelayCard
 */

if ( ! defined( 'ABSPATH' ) ) exit;

add_action( 'wp_ajax_relaycard_preview', 'relaycard_preview_handler' );

function relaycard_preview_handler() {
    check_ajax_referer( 'relaycard_preview', 'nonce' );
    if ( ! current_user_can( 'manage_options' ) ) wp_die( 'Unauthorized' );

    $options = get_option( 'relaycard_settings', [] );

    // Use a real recent post for the preview if available
    $recent = get_posts( [ 'posts_per_page' => 1, 'post_status' => 'publish' ] );
    $thumb  = ! empty( $recent ) ? get_the_post_thumbnail_url( $recent[0]->ID, 'medium_large' ) : '';
    $title  = ! empty( $recent ) ? $recent[0]->post_title : 'Your Post Title Will Appear Here';
    $link   = ! empty( $recent ) ? get_permalink( $recent[0]->ID ) : '#';

    // Use placeholder image if no thumb found
    if ( ! $thumb ) {
        $thumb = RELAYCARD_URL . 'assets/placeholder.png';
    }

    $html = relaycard_build_card( $thumb, $title, $link, $options );

    wp_send_json_success( [ 'html' => $html ] );
}

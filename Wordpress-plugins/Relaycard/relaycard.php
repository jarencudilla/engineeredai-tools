<?php
/*
 * Plugin Name:       EngineeredAI RelayCard — Inline Related Post Cards
 * Plugin URI:        https://engineeredai.net/relaycard
 * Description:       Inline post cards that read like ads, link like content. Image-dominant related post cards injected automatically into your content — heading-aware, config-driven, AI hook title generation optional.
 * Version:           1.0.1
 * Author:            EngineeredAI
 * Author URI:        https://engineeredai.net
 * License:           GPL2
 * License URI:       https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain:       relaycard
 */

/**
 * relaycard.php
 *
 * Plugin bootstrap. Registers hooks, loads files, enqueues assets.
 * Entry point for the entire RelayCard plugin.
 *
 * @package     RelayCard
 * @author      Jaren Cudilla / EngineeredAI
 * @link        https://engineeredai.net
 * @version     1.0.1
 */

if ( ! defined( 'ABSPATH' ) ) exit;

define( 'RELAYCARD_VERSION', '1.0.1' );
define( 'RELAYCARD_PATH', plugin_dir_path( __FILE__ ) );
define( 'RELAYCARD_URL', plugin_dir_url( __FILE__ ) );

// — Load modules —
require_once RELAYCARD_PATH . 'inc/related-query.php';
require_once RELAYCARD_PATH . 'inc/title-stack.php';
require_once RELAYCARD_PATH . 'inc/card-engine.php';
require_once RELAYCARD_PATH . 'inc/attribution.php';
require_once RELAYCARD_PATH . 'admin/admin-page.php';
require_once RELAYCARD_PATH . 'admin/preview-ajax.php';

// — Enqueue frontend CSS —
add_action( 'wp_enqueue_scripts', 'relaycard_enqueue_frontend_assets' );
function relaycard_enqueue_frontend_assets() {
    if ( ! is_single() ) {
        return;
    }
    wp_enqueue_style(
        'relaycard',
        RELAYCARD_URL . 'assets/relaycard.css',
        [],
        RELAYCARD_VERSION
    );
}

// — Enqueue admin assets —
add_action( 'admin_enqueue_scripts', 'relaycard_enqueue_admin_assets' );
function relaycard_enqueue_admin_assets( $hook ) {
    if ( $hook !== 'settings_page_relaycard' ) return;
    wp_enqueue_style(
        'relaycard-admin',
        RELAYCARD_URL . 'assets/relaycard-admin.css',
        [],
        RELAYCARD_VERSION
    );
    wp_enqueue_script(
        'relaycard-admin',
        RELAYCARD_URL . 'assets/relaycard-admin.js',
        [ 'jquery' ],
        RELAYCARD_VERSION,
        true
    );
    wp_localize_script( 'relaycard-admin', 'relaycardAdmin', [
        'ajaxUrl' => admin_url( 'admin-ajax.php' ),
        'nonce'   => wp_create_nonce( 'relaycard_preview' ),
    ] );
}

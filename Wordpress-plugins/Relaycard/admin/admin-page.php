<?php
/**
 * admin-page.php
 *
 * Registers RelayCard settings page under Settings menu.
 * Handles settings form save and renders admin UI.
 *
 * @package RelayCard
 */

if ( ! defined( 'ABSPATH' ) ) exit;

add_action( 'admin_menu', 'relaycard_admin_menu' );
function relaycard_admin_menu() {
    add_options_page(
        'RelayCard Settings',
        'RelayCard',
        'manage_options',
        'relaycard',
        'relaycard_admin_page'
    );
}

add_action( 'admin_init', 'relaycard_register_settings' );
function relaycard_register_settings() {
    register_setting( 'relaycard_settings_group', 'relaycard_settings', [
        'sanitize_callback' => 'relaycard_sanitize_settings',
    ] );
}

/**
 * relaycard_sanitize_settings
 * Sanitizes all settings before saving.
 */
function relaycard_sanitize_settings( $input ) {
    $clean = [];
    $allowed_styles = [ 'split', 'overlay', 'cinematic', 'minimal', 'story' ];
    $allowed_fonts  = [ 'sans', 'mono', 'script' ];
    $allowed_ratios = [ '50', '60', '70' ];
    $allowed_ai     = [ 'gemini', 'openai', 'claude', '' ];

    $clean['card_style']  = in_array( $input['card_style'] ?? 'split', $allowed_styles ) ? $input['card_style'] : 'split';
    $clean['font_cat']    = in_array( $input['font_cat'] ?? 'sans', $allowed_fonts ) ? $input['font_cat'] : 'sans';
    $clean['img_ratio']   = in_array( $input['img_ratio'] ?? '60', $allowed_ratios ) ? $input['img_ratio'] : '60';
    $clean['accent']      = sanitize_hex_color( $input['accent'] ?? '#e05a2b' );
    $clean['cta_text']    = sanitize_text_field( $input['cta_text'] ?? 'Read More →' );
    $clean['card_label']  = sanitize_text_field( $input['card_label'] ?? '' );
    $clean['ai_provider'] = in_array( $input['ai_provider'] ?? '', $allowed_ai ) ? $input['ai_provider'] : '';
    $clean['ai_key']      = sanitize_text_field( $input['ai_key'] ?? '' );

    return $clean;
}

/**
 * relaycard_admin_page
 * Renders the settings UI.
 */
function relaycard_admin_page() {
    $options = get_option( 'relaycard_settings', [] );
    $style   = $options['card_style']  ?? 'split';
    $font    = $options['font_cat']    ?? 'sans';
    $ratio   = $options['img_ratio']   ?? '60';
    $accent  = $options['accent']      ?? '#e05a2b';
    $cta     = $options['cta_text']    ?? 'Read More →';
    $label   = $options['card_label']  ?? '';
    $ai_prov = $options['ai_provider'] ?? '';
    $ai_key  = $options['ai_key']      ?? '';
    ?>
    <div class="wrap relaycard-admin">
        <h1>RelayCard <span class="relaycard-version">v<?php echo esc_html( RELAYCARD_VERSION ); ?></span></h1>
        <p class="relaycard-tagline">Inline post cards that read like ads, link like content. <a href="https://engineeredai.net" target="_blank">engineeredai.net</a></p>

        <div class="relaycard-admin-layout">

            <!-- Settings Column -->
            <div class="relaycard-admin-settings">
                <form method="post" action="options.php">
                    <?php settings_fields( 'relaycard_settings_group' ); ?>

                    <!-- Card Style -->
                    <div class="relaycard-section">
                        <h2>Card Style</h2>
                        <div class="relaycard-style-picker">
                            <?php
                            $styles = [
                                'split'     => 'Split — image left, text right',
                                'overlay'   => 'Overlay — full bleed with gradient',
                                'cinematic' => 'Cinematic — wide image, centered title',
                                'minimal'   => 'Minimal — no image, text only',
                                'story'     => 'Story — image top, text below',
                            ];
                            foreach ( $styles as $val => $label_text ) :
                            ?>
                            <label class="relaycard-style-option <?php echo $style === $val ? 'is-selected' : ''; ?>">
                                <input type="radio" name="relaycard_settings[card_style]" value="<?php echo esc_attr( $val ); ?>" <?php checked( $style, $val ); ?>>
                                <span class="relaycard-style-thumb relaycard-style-thumb--<?php echo esc_attr( $val ); ?>"></span>
                                <span class="relaycard-style-label"><?php echo esc_html( $label_text ); ?></span>
                            </label>
                            <?php endforeach; ?>
                        </div>
                    </div>

                    <!-- Image Ratio (split only) -->
                    <div class="relaycard-section">
                        <h2>Image Ratio <span class="relaycard-note">(split style only)</span></h2>
                        <div class="relaycard-ratio-picker">
                            <?php foreach ( [ '50' => '50 / 50', '60' => '60 / 40', '70' => '70 / 30' ] as $val => $lbl ) : ?>
                            <label class="relaycard-ratio-option <?php echo $ratio === $val ? 'is-selected' : ''; ?>">
                                <input type="radio" name="relaycard_settings[img_ratio]" value="<?php echo esc_attr( $val ); ?>" <?php checked( $ratio, $val ); ?>>
                                <?php echo esc_html( $lbl ); ?>
                            </label>
                            <?php endforeach; ?>
                        </div>
                    </div>

                    <!-- Font Category -->
                    <div class="relaycard-section">
                        <h2>Font Style</h2>
                        <div class="relaycard-font-picker">
                            <?php foreach ( [ 'sans' => 'Sans-serif', 'mono' => 'Monospace', 'script' => 'Script' ] as $val => $lbl ) : ?>
                            <label class="relaycard-font-option <?php echo $font === $val ? 'is-selected' : ''; ?>">
                                <input type="radio" name="relaycard_settings[font_cat]" value="<?php echo esc_attr( $val ); ?>" <?php checked( $font, $val ); ?>>
                                <span class="relaycard-font-preview relaycard-font-preview--<?php echo esc_attr( $val ); ?>"><?php echo esc_html( $lbl ); ?></span>
                            </label>
                            <?php endforeach; ?>
                        </div>
                    </div>

                    <!-- Accent Color -->
                    <div class="relaycard-section">
                        <h2>Accent Color</h2>
                        <input type="color" name="relaycard_settings[accent]" value="<?php echo esc_attr( $accent ); ?>" id="relaycard-accent">
                        <span class="relaycard-accent-hex"><?php echo esc_html( $accent ); ?></span>
                    </div>

                    <!-- CTA Text -->
                    <div class="relaycard-section">
                        <h2>CTA Text</h2>
                        <input type="text" name="relaycard_settings[cta_text]" value="<?php echo esc_attr( $cta ); ?>" class="regular-text" placeholder="Read More →">
                    </div>

                    <!-- Card Label -->
                    <div class="relaycard-section">
                        <h2>Card Label <span class="relaycard-note">(optional)</span></h2>
                        <input type="text" name="relaycard_settings[card_label]" value="<?php echo esc_attr( $label ); ?>" class="regular-text" placeholder="e.g. // related">
                    </div>

                    <!-- AI Hook Title -->
                    <div class="relaycard-section">
                        <h2>AI Hook Title Generation <span class="relaycard-note">(optional — BYOK)</span></h2>
                        <p class="description">Generate punchy hook titles automatically. Bring your own API key.</p>
                        <select name="relaycard_settings[ai_provider]" id="relaycard-ai-provider">
                            <option value="" <?php selected( $ai_prov, '' ); ?>>Disabled</option>
                            <option value="gemini" <?php selected( $ai_prov, 'gemini' ); ?>>Gemini (Google AI Studio — free tier available)</option>
                            <option value="openai" <?php selected( $ai_prov, 'openai' ); ?>>ChatGPT (OpenAI — paid)</option>
                            <option value="claude" <?php selected( $ai_prov, 'claude' ); ?>>Claude (Anthropic — paid)</option>
                        </select>
                        <input type="password" name="relaycard_settings[ai_key]" value="<?php echo esc_attr( $ai_key ); ?>" class="regular-text" placeholder="Paste API key here" style="margin-top:0.5rem;">
                    </div>

                    <?php submit_button( 'Save Settings' ); ?>
                </form>
            </div>

            <!-- Live Preview Column -->
            <div class="relaycard-admin-preview">
                <h2>Preview</h2>
                <div id="relaycard-preview-frame">
                    <p class="relaycard-preview-placeholder">Save settings to see preview.</p>
                </div>
                <button type="button" id="relaycard-preview-btn" class="button button-secondary">Refresh Preview</button>
            </div>

        </div><!-- .relaycard-admin-layout -->
    </div>
    <?php
}
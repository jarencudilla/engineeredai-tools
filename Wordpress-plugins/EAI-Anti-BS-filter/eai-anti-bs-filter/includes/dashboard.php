<?php
/**
 * includes/dashboard.php
 *
 * Admin Settings page under Settings -> EAI Anti-BS Filter. Lets the
 * moderator toggle auto-approve / pro mode and edit the roast persona and
 * line pools (textarea -> array, one per line).
 * Depends on: settings.php (EAI_ABS_OPTION, eai_abs_get_settings).
 */
defined('ABSPATH') || exit;

add_action('admin_menu', function () {
    add_options_page(
        __('EAI Anti-BS Filter', 'eai-anti-bs-filter'),
        __('EAI Anti-BS Filter', 'eai-anti-bs-filter'),
        'manage_options',
        'eai-abs-settings',
        'eai_abs_render_settings_page'
    );
});

add_action('admin_init', function () {
    register_setting('eai_abs_group', EAI_ABS_OPTION, [
        'type'              => 'array',
        'sanitize_callback' => 'eai_abs_sanitize_options',
        'default'           => eai_abs_default_settings(),
    ]);
});

/**
 * eai_abs_sanitize_options
 * Settings API sanitize callback — validates checkbox bools and splits the
 * persona/line textareas into arrays.
 * @param  array $input Raw $_POST settings array.
 * @return array Sanitized settings, ready to save.
 */
function eai_abs_sanitize_options($input) {
    $out = eai_abs_default_settings();
    $out['auto_approve'] = !empty($input['auto_approve']);
    $out['pro_mode']     = !empty($input['pro_mode']);

    $out['personas'] = array_values(array_filter(array_map('sanitize_text_field',
        preg_split('/\r\n|\r|\n/', $input['personas'] ?? '')
    )));
    $out['lines'] = array_values(array_filter(array_map('wp_kses_post',
        preg_split('/\r\n|\r|\n/', $input['lines'] ?? '')
    )));

    return $out;
}

/**
 * eai_abs_render_settings_page
 * Outputs the Settings page form. Prefills personas/lines from the bundled
 * JSON defaults if no custom values have been saved yet.
 * @return void
 */
function eai_abs_render_settings_page() {
    if (!current_user_can('manage_options')) {
        return;
    }

    $s = eai_abs_get_settings();

    if (empty($s['personas'])) {
        $p = EAI_ABS_PLUGIN_DIR . 'logs/roast_personas.json';
        if (file_exists($p)) {
            $arr = json_decode(file_get_contents($p), true);
            if (is_array($arr) && $arr) {
                $s['personas'] = $arr;
            }
        }
    }
    if (empty($s['lines'])) {
        $p = EAI_ABS_PLUGIN_DIR . 'logs/roast_lines.json';
        if (file_exists($p)) {
            $arr = json_decode(file_get_contents($p), true);
            if (is_array($arr) && $arr) {
                $s['lines'] = $arr;
            }
        }
    }
    ?>
    <div class="wrap">
        <h1><?php esc_html_e('EAI Anti-BS Filter', 'eai-anti-bs-filter'); ?></h1>
        <form method="post" action="options.php">
            <?php settings_fields('eai_abs_group'); ?>
            <table class="form-table" role="presentation">
                <tbody>
                    <tr>
                        <th scope="row"><?php esc_html_e('Auto-approve sanitized roasts', 'eai-anti-bs-filter'); ?></th>
                        <td>
                            <label>
                                <input type="checkbox" name="<?php echo esc_attr(EAI_ABS_OPTION); ?>[auto_approve]" value="1" <?php checked($s['auto_approve']); ?> />
                                <?php esc_html_e('Approve sanitized comments immediately', 'eai-anti-bs-filter'); ?>
                            </label>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><?php esc_html_e('Pro / No-linkback', 'eai-anti-bs-filter'); ?></th>
                        <td>
                            <label>
                                <input type="checkbox" name="<?php echo esc_attr(EAI_ABS_OPTION); ?>[pro_mode]" value="1" <?php checked($s['pro_mode']); ?> />
                                <?php esc_html_e('Remove the EAI linkback from the roast footer', 'eai-anti-bs-filter'); ?>
                            </label>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><?php esc_html_e('Roast Personas', 'eai-anti-bs-filter'); ?></th>
                        <td>
                            <textarea name="<?php echo esc_attr(EAI_ABS_OPTION); ?>[personas]" rows="6" style="width:100%;"><?php
                                echo esc_textarea(implode("\n", $s['personas']));
                            ?></textarea>
                            <p class="description"><?php esc_html_e('One persona per line.', 'eai-anti-bs-filter'); ?></p>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><?php esc_html_e('Roast Lines', 'eai-anti-bs-filter'); ?></th>
                        <td>
                            <textarea name="<?php echo esc_attr(EAI_ABS_OPTION); ?>[lines]" rows="10" style="width:100%;"><?php
                                echo esc_textarea(implode("\n", $s['lines']));
                            ?></textarea>
                            <p class="description"><?php esc_html_e('One roast line per line. Basic HTML allowed; keep it short.', 'eai-anti-bs-filter'); ?></p>
                        </td>
                    </tr>
                </tbody>
            </table>
            <?php submit_button(__('Save Settings', 'eai-anti-bs-filter')); ?>
        </form>
    </div>
    <?php
}

<?php
defined('ABSPATH') || exit;

add_action('admin_menu', function () {
    add_options_page(
        'EAI Anti-BS Filter',
        'EAI Anti-BS Filter',
        'manage_options',
        'eai-anti-bs',
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

function eai_abs_sanitize_options($input) {
    $out = eai_abs_default_settings();
    $out['auto_approve'] = !empty($input['auto_approve']);
    $out['pro_mode']     = !empty($input['pro_mode']);

    // Textareas -> arrays (one per line)
    $out['personas'] = array_values(array_filter(array_map('trim',
        preg_split('/\r\n|\r|\n/', $input['personas'] ?? '')
    )));
    $out['lines']    = array_values(array_filter(array_map('trim',
        preg_split('/\r\n|\r|\n/', $input['lines'] ?? '')
    )));

    return $out;
}

function eai_abs_render_settings_page() {
    if (!current_user_can('manage_options')) return;

    // Current saved settings
    $s = eai_abs_get_settings();

    // Prefill from JSON if settings are empty
    if (empty($s['personas'])) {
        $p = plugin_dir_path(__FILE__) . '../logs/roast_personas.json';
        if (file_exists($p)) {
            $arr = json_decode(file_get_contents($p), true);
            if (is_array($arr) && $arr) $s['personas'] = $arr;
        }
    }
    if (empty($s['lines'])) {
        $p = plugin_dir_path(__FILE__) . '../logs/roast_lines.json';
        if (file_exists($p)) {
            $arr = json_decode(file_get_contents($p), true);
            if (is_array($arr) && $arr) $s['lines'] = $arr;
        }
    }
    ?>
    <div class="wrap">
      <h1>EAI Anti-BS Filter</h1>
      <form method="post" action="options.php">
        <?php settings_fields('eai_abs_group'); ?>
        <table class="form-table" role="presentation">
          <tbody>
            <tr>
              <th scope="row">Auto-approve sanitized roasts</th>
              <td>
                <label>
                  <input type="checkbox" name="<?php echo esc_attr(EAI_ABS_OPTION); ?>[auto_approve]" value="1" <?php checked($s['auto_approve']); ?> />
                  Approve sanitized comments immediately
                </label>
              </td>
            </tr>
            <tr>
              <th scope="row">Pro / No-linkback</th>
              <td>
                <label>
                  <input type="checkbox" name="<?php echo esc_attr(EAI_ABS_OPTION); ?>[pro_mode]" value="1" <?php checked($s['pro_mode']); ?> />
                  Remove linkback (set this after you’ve donated $5)
                </label>
              </td>
            </tr>
            <tr>
              <th scope="row">Roast Personas</th>
              <td>
                <textarea name="<?php echo esc_attr(EAI_ABS_OPTION); ?>[personas]" rows="6" style="width: 100%;"><?php
                    echo esc_textarea(implode("\n", $s['personas']));
                ?></textarea>
                <p class="description">One persona per line (e.g., “Sir Spam-a-lot”).</p>
              </td>
            </tr>
            <tr>
              <th scope="row">Roast Lines</th>
              <td>
                <textarea name="<?php echo esc_attr(EAI_ABS_OPTION); ?>[lines]" rows="10" style="width: 100%;"><?php
                    echo esc_textarea(implode("\n", $s['lines']));
                ?></textarea>
                <p class="description">One roast line per line. HTML allowed but keep it short.</p>
              </td>
            </tr>
          </tbody>
        </table>
        <?php submit_button('Save Settings'); ?>
      </form>
    </div>
    <?php
}

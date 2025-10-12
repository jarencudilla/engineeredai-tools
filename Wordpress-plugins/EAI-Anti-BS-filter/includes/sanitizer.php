<?php
defined('ABSPATH') || exit;

/**
 * === EAI Anti-BS – Sanitizer ===
 * Detects spam using fingerprints + additional pattern matching
 * Sanitizes spam comments by replacing with roasts
 * Learns from manually flagged spam
 */

// Debug logging (set to false in production)
if (!defined('EAI_ABS_DEBUG')) define('EAI_ABS_DEBUG', true);

/**
 * Enhanced spam detection with multiple indicators
 */
function eai_is_spam_comment($comment) {
    $content = is_array($comment)
        ? strtolower($comment['comment_content'] ?? '')
        : strtolower(($comment instanceof WP_Comment) ? $comment->comment_content : '');
    
    $email = is_array($comment)
        ? strtolower($comment['comment_author_email'] ?? '')
        : strtolower(($comment instanceof WP_Comment) ? $comment->comment_author_email : '');
    
    $url = is_array($comment)
        ? strtolower($comment['comment_author_url'] ?? '')
        : strtolower(($comment instanceof WP_Comment) ? $comment->comment_author_url : '');
    
    // Quick spam pattern checks
    $indicators = [
        'outlook_email' => strpos($email, 'outlook.com') !== false,
        'binance' => strpos($content . $url, 'binance') !== false,
        'gate_io' => strpos($content . $url, 'gate.') !== false,
        'referral' => preg_match('/ref=|register\?|signup\?ref/i', $content . $url),
        'spam_phrases' => preg_match('/(your article helped me|is there any more related content|i have a question for you|can you help me|thanks for sharing|i read many of your blog posts)/i', $content),
        'generic_praise' => preg_match('/(very good|cool.*blog|thank you for your sharing)/i', $content) && strlen($content) < 150,
    ];
    
    $quick_match = in_array(true, $indicators, true);
    
    if (EAI_ABS_DEBUG && $quick_match) {
        $matched = array_keys(array_filter($indicators));
        error_log('[EAI] 🎯 Spam detected via: ' . implode(', ', $matched));
    }
    
    // Also check learned fingerprints
    if (!$quick_match && function_exists('eai_comment_matches_fingerprint')) {
        $quick_match = eai_comment_matches_fingerprint($comment);
        if (EAI_ABS_DEBUG && $quick_match) {
            error_log('[EAI] 🎯 Spam detected via fingerprint matcher');
        }
    }
    
    return $quick_match;
}

/**
 * PRE-INSERT: Catch and sanitize spam BEFORE it enters the database
 */
add_filter('preprocess_comment', function ($commentdata) {
    // Skip trackbacks/pingbacks and logged-in admins
    if (($commentdata['comment_type'] ?? '') !== 'comment' || current_user_can('moderate_comments')) {
        return $commentdata;
    }
    
    if (EAI_ABS_DEBUG) {
        error_log('[EAI] 🔍 Checking comment from: ' . ($commentdata['comment_author'] ?? 'unknown') . 
                  ' <' . ($commentdata['comment_author_email'] ?? 'unknown') . '>');
    }
    
    // Check if it's spam
    if (!eai_is_spam_comment($commentdata)) {
        if (EAI_ABS_DEBUG) error_log('[EAI] ✅ Clean comment - allowing through');
        return $commentdata;
    }
    
    if (EAI_ABS_DEBUG) error_log('[EAI] 🔥 SPAM DETECTED - sanitizing');
    
    // Save original data
    $original = $commentdata;
    
    // Get roast content
    $phrase  = function_exists('eai_get_random_phrase') 
        ? eai_get_random_phrase($commentdata['comment_post_ID'] ?? 0) 
        : "This was spam. It got rebooted.";
    $persona = function_exists('eai_get_fake_author') 
        ? eai_get_fake_author() 
        : "Anonymous Roasted";
    $footer  = function_exists('eai_roast_footer_html') 
        ? eai_roast_footer_html() 
        : 'Sanitized by EAI Anti-BS Bot™';
    
    // Replace with sanitized version
    $commentdata['comment_content']      = "[Filtered by EAI Anti-BS Bot™]\n\n<blockquote>{$phrase}</blockquote>\n\n<small>{$footer}</small>";
    $commentdata['comment_author']       = $persona;
    $commentdata['comment_author_email'] = 'sanitized@eai.internal';
    $commentdata['comment_author_url']   = '';
    $commentdata['comment_agent']        = trim(($commentdata['comment_agent'] ?? '') . ' EAI-SANITIZED');
    
    // Auto-approve based on settings
    if (function_exists('eai_abs_get') && eai_abs_get('auto_approve', true)) {
        $commentdata['comment_approved'] = 1;
        if (EAI_ABS_DEBUG) error_log('[EAI] ✅ Auto-approved roasted comment');
    }
    
    // After comment is inserted, save metadata and train
    add_action('comment_post', function ($cid) use ($original) {
        if (EAI_ABS_DEBUG) error_log('[EAI] 📝 Saving spam metadata for comment_id=' . $cid);
        
        // Mark as sanitized
        add_comment_meta($cid, 'eai_sanitized', true, true);
        
        // Save original spam for learning
        add_comment_meta($cid, 'eai_original_spam', json_encode([
            'author' => $original['comment_author'] ?? '',
            'email' => $original['comment_author_email'] ?? '',
            'url' => $original['comment_author_url'] ?? '',
            'content' => $original['comment_content'] ?? '',
            'ip' => $original['comment_author_IP'] ?? '',
            'agent' => $original['comment_agent'] ?? '',
            'timestamp' => current_time('mysql'),
            'auto_detected' => true
        ]), true);
        
        // Log to spam database
        if (function_exists('eai_log_spam')) {
            eai_log_spam($original, ['comment_content' => 'ROASTED'], 'auto_sanitized_preinsert');
        }
        
        // Train from this spam
        if (function_exists('eai_add_spam_fingerprint')) {
            eai_add_spam_fingerprint($original);
            if (EAI_ABS_DEBUG) error_log('[EAI] 📚 Trained from auto-detected spam');
        }
    }, 10, 1);
    
    return $commentdata;
}, 9);

/**
 * POST-INSERT: Sanitize comments that land as spam (from Akismet, etc.)
 */
function eai_sanitize_existing_comment($comment) {
    if (!($comment instanceof WP_Comment)) {
        if (EAI_ABS_DEBUG) error_log('[EAI] ⚠️ Invalid comment object passed to sanitizer');
        return;
    }
    
    if (EAI_ABS_DEBUG) {
        error_log('[EAI] 🔧 Post-insert sanitizer for comment_id=' . $comment->comment_ID . 
                  ' (status: ' . wp_get_comment_status($comment->comment_ID) . ')');
    }
    
    // Already sanitized?
    if (get_comment_meta($comment->comment_ID, 'eai_sanitized', true)) {
        if (EAI_ABS_DEBUG) error_log('[EAI] ⏭️ Already sanitized, skipping');
        return;
    }
    
    // Save original before sanitizing
    $original = [
        'author' => $comment->comment_author,
        'email' => $comment->comment_author_email,
        'url' => $comment->comment_author_url,
        'content' => $comment->comment_content,
        'ip' => $comment->comment_author_IP,
        'agent' => $comment->comment_agent,
        'timestamp' => current_time('mysql')
    ];
    
    update_comment_meta($comment->comment_ID, 'eai_original_spam', json_encode($original));
    
    // Get roast content
    $phrase  = function_exists('eai_get_random_phrase') 
        ? eai_get_random_phrase($comment->comment_post_ID) 
        : "This was spam. It got rebooted.";
    $persona = function_exists('eai_get_fake_author') 
        ? eai_get_fake_author() 
        : "Anonymous Roasted";
    $footer  = function_exists('eai_roast_footer_html') 
        ? eai_roast_footer_html() 
        : 'Sanitized by EAI Anti-BS Bot™';
    
    // Update the comment
    wp_update_comment([
        'comment_ID'          => $comment->comment_ID,
        'comment_content'     => "[Filtered by EAI Anti-BS Bot™]\n\n<blockquote>{$phrase}</blockquote>\n\n<small>{$footer}</small>",
        'comment_author'      => $persona,
        'comment_author_email' => 'sanitized@eai.internal',
        'comment_author_url'  => '',
        'comment_agent'       => trim(($comment->comment_agent ?? '') . ' EAI-SANITIZED'),
    ]);
    
    // Set status based on settings
    if (function_exists('eai_abs_get') && eai_abs_get('auto_approve', true)) {
        wp_set_comment_status($comment->comment_ID, 'approve');
        if (EAI_ABS_DEBUG) error_log('[EAI] ✅ Auto-approved post-insert roast');
    } else {
        wp_set_comment_status($comment->comment_ID, 'hold');
        if (EAI_ABS_DEBUG) error_log('[EAI] 🕒 Set to pending for moderation');
    }
    
    update_comment_meta($comment->comment_ID, 'eai_sanitized', true);
    
    // Train from this spam
    if (function_exists('eai_add_spam_fingerprint')) {
        eai_add_spam_fingerprint($original);
    }
    
    // Log
    if (function_exists('eai_log_spam')) {
        eai_log_spam($original, (array)$comment, 'post_insert_sanitized');
    }
    
    if (EAI_ABS_DEBUG) {
        error_log('[EAI] 🔥 Successfully sanitized comment_id=' . $comment->comment_ID);
    }
}

/**
 * Hook: Catch comments transitioning TO spam
 */
add_action('transition_comment_status', function ($new_status, $old_status, $comment) {
    if ('spam' === $new_status && 'spam' !== $old_status) {
        if (EAI_ABS_DEBUG) {
            error_log('[EAI] 📬 Comment transitioned to spam: comment_id=' . $comment->comment_ID);
        }
        eai_sanitize_existing_comment($comment);
    }
}, 10, 3);

/**
 * Hook: Catch comments inserted DIRECTLY as spam
 */
add_action('comment_post', function ($comment_id, $approved) {
    if ($approved === 'spam' || $approved === 0) {
        $comment = get_comment($comment_id);
        if ($comment && !get_comment_meta($comment_id, 'eai_sanitized', true)) {
            if (EAI_ABS_DEBUG) {
                error_log('[EAI] 📬 Comment inserted as spam: comment_id=' . $comment_id);
            }
            eai_sanitize_existing_comment($comment);
        }
    }
}, 99, 2);

/**
 * Add spam fingerprint to learning database
 */
function eai_add_spam_fingerprint($spam_data) {
    $content = is_array($spam_data) 
        ? strtolower($spam_data['content'] ?? $spam_data['comment_content'] ?? '')
        : '';
    $email = is_array($spam_data)
        ? strtolower($spam_data['email'] ?? $spam_data['comment_author_email'] ?? '')
        : '';
    $url = is_array($spam_data)
        ? strtolower($spam_data['url'] ?? $spam_data['comment_author_url'] ?? '')
        : '';
    
    if (!$content) return;
    
    $fp = get_option(EAI_FP_OPTION, ['keywords' => [], 'domains' => [], 'emails' => [], 'ts' => time()]);
    
    // Extract and save domains
    preg_match_all('/[a-z0-9\.\-]{3,}\.[a-z]{2,6}/i', $content . ' ' . $url, $domains);
    foreach ($domains[0] as $d) {
        $d = strtolower($d);
        if (!in_array($d, $fp['domains'] ?? [])) {
            $fp['domains'][] = $d;
        }
    }
    
    // Extract keywords
    $suspicious_words = ['binance', 'crypto', 'usdt', 'gate', 'register', 'ref=', 'telegram', 'whatsapp', 
                        'forex', 'casino', 'loan', 'betting', 'viagra', 'cialis'];
    foreach ($suspicious_words as $word) {
        if (strpos($content . $url, $word) !== false && !in_array($word, $fp['keywords'] ?? [])) {
            $fp['keywords'][] = $word;
        }
    }
    
    // Save email domain if suspicious
    if ($email && strpos($email, '@') !== false) {
        $email_domain = substr($email, strpos($email, '@') + 1);
        if ($email_domain && !in_array($email_domain, $fp['emails'] ?? [])) {
            $fp['emails'][] = $email_domain;
        }
    }
    
    $fp['ts'] = time();
    update_option(EAI_FP_OPTION, $fp, false);
    
    if (EAI_ABS_DEBUG) {
        error_log('[EAI] 📚 Updated fingerprints: ' . 
                  count($fp['keywords']) . ' keywords, ' . 
                  count($fp['domains']) . ' domains, ' .
                  count($fp['emails'] ?? []) . ' email domains');
    }
}
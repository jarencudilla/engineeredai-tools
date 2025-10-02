<?php
defined('ABSPATH') || exit;

const EAI_FP_OPTION = 'eai_anti_bs_fingerprints_v1';

function eai_default_keywords() {
    return ['binance','crypto','usdt','telegram','whatsapp','forex','loan','casino','betting','click here',
            'gate.io','gate.com','ref=','register?','signup'];
}

function eai_train_from_comments() {
    $patterns = ['keywords'=>[],'domains'=>[],'emails'=>[]];

    $spam = get_comments(['status'=>'spam','number'=>200]);
    $hold = get_comments(['status'=>'hold','number'=>200]);
    $candidates = array_merge($spam,$hold);

    foreach ($candidates as $c) {
        $txt = strtolower(wp_strip_all_tags($c->comment_content));
        $email = strtolower($c->comment_author_email);

        // catch domains from content and URL
        preg_match_all('/[a-z0-9\.\-]{3,}\.[a-z]{2,6}/i', $txt . ' ' . $c->comment_author_url, $domains);
        foreach ($domains[0] as $d) { 
            $patterns['domains'][strtolower($d)] = 1; 
        }

        // catch email domains
        if ($email && strpos($email, '@') !== false) {
            $email_domain = substr($email, strpos($email, '@') + 1);
            if ($email_domain) {
                $patterns['emails'][$email_domain] = 1;
            }
        }

        // suspicious keywords
        $suspicious = ['binance','crypto','usdt','telegram','whatsapp','forex','loan','casino','porn',
                      'betting','viagra','cialis','gate.io','gate.com','ref=','register'];
        foreach ($suspicious as $kw) {
            if (strpos($txt, $kw) !== false) $patterns['keywords'][$kw] = 1;
        }
    }

    // Add defaults
    foreach (eai_default_keywords() as $kw) { 
        $patterns['keywords'][$kw] = 1; 
    }

    $save = [
        'keywords' => array_keys($patterns['keywords']),
        'domains' => array_keys($patterns['domains']),
        'emails' => array_keys($patterns['emails']),
        'ts' => time()
    ];
    update_option(EAI_FP_OPTION, $save, false);
    error_log('[EAI] 📚 Trained from ' . count($candidates) . ' comments: ' . 
              count($save['keywords']) . ' keywords, ' . 
              count($save['domains']) . ' domains, ' .
              count($save['emails']) . ' email domains');
    return $save;
}

function eai_get_fingerprints() {
    $fp = get_option(EAI_FP_OPTION);
    if (!$fp || !is_array($fp)) {
        $fp = eai_train_from_comments();
    }
    return $fp;
}

function eai_comment_matches_fingerprint($comment) {
    $content = is_array($comment) 
        ? strtolower($comment['comment_content'] ?? '') 
        : strtolower($comment->comment_content);
    
    $email = is_array($comment)
        ? strtolower($comment['comment_author_email'] ?? '')
        : strtolower($comment->comment_author_email);
    
    $url = is_array($comment)
        ? strtolower($comment['comment_author_url'] ?? '')
        : strtolower($comment->comment_author_url);
    
    $fp = eai_get_fingerprints();

    // Too many links = spam
    if (preg_match_all('#https?://#i', $content) >= 2) {
        return true;
    }

    // Check keywords
    foreach ($fp['keywords'] ?? [] as $kw) {
        if ($kw && strpos($content . ' ' . $url, $kw) !== false) {
            return true;
        }
    }
    
    // Check domains
    foreach ($fp['domains'] ?? [] as $d) {
        if ($d && strpos($content . ' ' . $url, $d) !== false) {
            return true;
        }
    }
    
    // Check email domains
    if ($email && strpos($email, '@') !== false) {
        $email_domain = substr($email, strpos($email, '@') + 1);
        if (in_array($email_domain, $fp['emails'] ?? [])) {
            return true;
        }
    }

    return false;
}
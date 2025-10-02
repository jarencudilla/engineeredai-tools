<?php
defined('ABSPATH') || exit;

const EAI_FP_OPTION = 'eai_anti_bs_fingerprints_v1';

function eai_default_keywords() {
    return ['binance','crypto','usdt','telegram','whatsapp','forex','loan','casino','betting','click here'];
}

function eai_train_from_comments() {
    $patterns = ['keywords'=>[],'domains'=>[],'phones'=>[]];

    $spam = get_comments(['status'=>'spam','number'=>200]);
    $hold = get_comments(['status'=>'hold','number'=>200]);
    $candidates = array_merge($spam,$hold);

    foreach ($candidates as $c) {
        $txt = strtolower(wp_strip_all_tags($c->comment_content));

        // catch domains
        preg_match_all('/[a-z0-9\.\-]{3,}\.[a-z]{2,6}/i',$txt,$domains);
        foreach ($domains[0] as $d) { $patterns['domains'][strtolower($d)] = 1; }

        // suspicious keywords
        foreach (['binance','crypto','usdt','telegram','whatsapp','forex','loan','casino','porn'] as $kw) {
            if (strpos($txt,$kw)!==false) $patterns['keywords'][$kw]=1;
        }
    }

    foreach (eai_default_keywords() as $kw) { $patterns['keywords'][$kw]=1; }

    $save = [
        'keywords'=>array_keys($patterns['keywords']),
        'domains'=>array_keys($patterns['domains']),
        'ts'=>time()
    ];
    update_option(EAI_FP_OPTION,$save,false);
    return $save;
}

function eai_get_fingerprints() {
    $fp=get_option(EAI_FP_OPTION);
    if(!$fp||!is_array($fp)) $fp=eai_train_from_comments();
    return $fp;
}

function eai_comment_matches_fingerprint($comment) {
    $content = is_array($comment) ? strtolower($comment['comment_content']??'') : strtolower($comment->comment_content);
    $fp = eai_get_fingerprints();

    // too many links
    if (preg_match_all('#https?://#i',$content) >= 2) return true;

    // keyword/domain match
    foreach($fp['keywords']??[] as $kw){ if($kw && strpos($content,$kw)!==false) return true; }
    foreach($fp['domains']??[] as $d){ if($d && strpos($content,$d)!==false) return true; }

    return false;
}

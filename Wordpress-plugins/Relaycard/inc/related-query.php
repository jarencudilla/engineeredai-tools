<?php
/**
 * related-query.php
 *
 * Fetches related posts by category.
 * Returns array of post data arrays — no WP globals touched outside this file.
 *
 * @package RelayCard
 */

if ( ! defined( 'ABSPATH' ) ) exit;

/**
 * relaycard_get_related_posts
 * Queries posts in the same category as $post_id.
 *
 * @param  int  $post_id     Current post ID to exclude.
 * @param  int  $max_cards   How many related posts to fetch.
 * @return array             Array of [ thumb, title, link ] or empty.
 */
function relaycard_get_related_posts( $post_id, $max_cards ) {
    $cats = get_the_category( $post_id );
    if ( empty( $cats ) ) return [];

    $cat_ids = array_map( function( $c ) { return $c->term_id; }, $cats );

    $q = new WP_Query( [
        'posts_per_page'      => $max_cards + 2, // fetch extra to account for missing thumbs
        'post__not_in'        => [ $post_id ],
        'category__in'        => $cat_ids,
        'orderby'             => 'rand',
        'ignore_sticky_posts' => true,
        'no_found_rows'       => true,
    ] );

    $results = [];

    while ( $q->have_posts() ) {
        $q->the_post();
        $thumb = get_the_post_thumbnail_url( null, 'medium_large' );
        if ( ! $thumb ) continue; // skip posts with no image — card requires visual

        $results[] = [
            'thumb' => $thumb,
            'title' => get_the_title(),
            'link'  => get_permalink(),
            'id'    => get_the_ID(),
        ];

        if ( count( $results ) >= $max_cards ) break;
    }

    wp_reset_postdata();
    return $results;
}

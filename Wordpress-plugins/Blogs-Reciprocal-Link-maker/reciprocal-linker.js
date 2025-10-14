<?php
/**
 * Topic-Based Reciprocal Link Manager
 * Matches posts across blogs based on shared topics/tags
 * Scans feed content to identify topics, then links semantically related posts
 */

class Topic_Reciprocal_Link_Manager {
    
    private $all_blogs = array(
        'qajourney' => array(
            'name' => 'QA Journey',
            'feed' => 'https://qajourney.net/feed/',
            'domain' => 'qajourney.net',
        ),
        'engineered_ai' => array(
            'name' => 'Engineered AI',
            'feed' => 'https://engineeredai.net/feed/',
            'domain' => 'engineeredai.net',
        ),
        'momentum_path' => array(
            'name' => 'Momentum Path',
            'feed' => 'https://momentumpath.net/feed/',
            'domain' => 'momentumpath.net',
        ),
        'remote_work_haven' => array(
            'name' => 'Remote Work Haven',
            'feed' => 'https://remoteworkhaven.net/feed/',
            'domain' => 'remoteworkhaven.net',
        ),
        'healthy_forge' => array(
            'name' => 'Healthy Forge',
            'feed' => 'https://healthyforge.com/feed/',
            'domain' => 'healthyforge.com',
        ),
    );
    
    // Core topics to detect across all blogs
    private $topic_keywords = array(
        'qa' => array( 'qa', 'quality assurance', 'testing', 'test', 'automation', 'cypress', 'selenium', 'bug', 'defect' ),
        'remote-work' => array( 'remote', 'work from home', 'wfh', 'distributed', 'async', 'virtual', 'home office' ),
        'ai' => array( 'ai', 'artificial intelligence', 'machine learning', 'ml', 'automation', 'algorithm', 'neural', 'gpt' ),
        'career' => array( 'career', 'job', 'leadership', 'promotion', 'salary', 'skills', 'developer', 'engineer', 'lead', 'manager' ),
        'wellness' => array( 'wellness', 'health', 'mental health', 'burnout', 'stress', 'mindfulness', 'exercise', 'sleep' ),
        'productivity' => array( 'productivity', 'efficiency', 'workflow', 'time management', 'focus', 'procrastination', 'tools' ),
        'learning' => array( 'learning', 'training', 'education', 'course', 'tutorial', 'guide', 'best practices', 'tips' ),
    );
    
    private $current_blog_key = null;
    private $cache_duration = 3600;
    
    public function __construct() {
        $this->current_blog_key = $this->get_current_blog_key();
        
        add_filter( 'the_content', array( $this, 'inject_reciprocal_links' ), 99 );
        add_action( 'admin_menu', array( $this, 'add_admin_menu' ) );
        add_action( 'wp_ajax_topic_bulk_scan', array( $this, 'ajax_bulk_scan' ) );
        add_action( 'wp_ajax_topic_single_scan', array( $this, 'ajax_single_scan' ) );
    }
    
    private function get_current_blog_key() {
        $site_url = get_site_url();
        foreach ( $this->all_blogs as $key => $blog ) {
            if ( strpos( $site_url, $blog['domain'] ) !== false ) {
                return $key;
            }
        }
        return 'remote_work_haven';
    }
    
    private function get_external_blogs() {
        $external = array();
        foreach ( $this->all_blogs as $key => $blog ) {
            if ( $key !== $this->current_blog_key ) {
                $external[ $key ] = $blog;
            }
        }
        return $external;
    }
    
    public function add_admin_menu() {
        add_management_page(
            'Topic Link Scanner',
            'Topic Links',
            'manage_options',
            'topic_links',
            array( $this, 'render_admin_page' )
        );
    }
    
    public function render_admin_page() {
        ?>
        <div class="wrap">
            <h1>Topic-Based Reciprocal Link Scanner</h1>
            <p>Match posts across your network based on shared topics. Scans feed content to identify topics, then links semantically related posts.</p>
            
            <div id="scan-status" style="margin: 20px 0; padding: 15px; background: #f0f0f0; display: none;">
                <p id="status-text"></p>
                <div id="progress-bar" style="width: 100%; background: #ddd; height: 20px; border-radius: 4px; overflow: hidden;">
                    <div id="progress-fill" style="background: #0073aa; height: 100%; width: 0%; transition: width 0.3s;"></div>
                </div>
                <p id="progress-text" style="margin-top: 10px; font-size: 0.9em;"></p>
            </div>
            
            <form id="bulk-scan-form" style="background: #fff; padding: 15px; border: 1px solid #ddd; border-radius: 4px; max-width: 500px;">
                <table class="form-table">
                    <tr>
                        <th><label for="post_type">Post Type:</label></th>
                        <td>
                            <select name="post_type" id="post_type">
                                <option value="post">Posts</option>
                                <option value="page">Pages</option>
                            </select>
                        </td>
                    </tr>
                    <tr>
                        <th><label for="batch_size">Batch Size:</label></th>
                        <td>
                            <input type="number" name="batch_size" id="batch_size" value="10" min="1" max="50" />
                        </td>
                    </tr>
                </table>
                
                <button type="submit" class="button button-primary">Start Bulk Scan</button>
            </form>
            
            <hr />
            
            <h2>Single Post Scan</h2>
            <form id="single-scan-form">
                <input type="number" name="post_id" placeholder="Enter post ID" required />
                <button type="submit" class="button button-primary">Scan Post</button>
            </form>
        </div>
        
        <script>
        jQuery(function($) {
            let scanInProgress = false;
            let offset = 0;
            let totalPosts = 0;
            let scannedPosts = 0;
            
            $('#bulk-scan-form').on('submit', function(e) {
                e.preventDefault();
                if (scanInProgress) return;
                
                scanInProgress = true;
                offset = 0;
                scannedPosts = 0;
                
                const postType = $('#post_type').val();
                const batchSize = parseInt($('#batch_size').val()) || 10;
                
                $('#scan-status').show();
                $('#status-text').text('Fetching posts...');
                
                $.ajax({
                    url: ajaxurl,
                    type: 'POST',
                    data: {
                        action: 'topic_bulk_scan',
                        mode: 'count',
                        post_type: postType,
                    },
                    success: function(res) {
                        if (res.success) {
                            totalPosts = res.data.total;
                            $('#progress-text').text('0 / ' + totalPosts);
                            scanBatch(postType, batchSize);
                        }
                    }
                });
            });
            
            function scanBatch(postType, batchSize) {
                $.ajax({
                    url: ajaxurl,
                    type: 'POST',
                    data: {
                        action: 'topic_bulk_scan',
                        mode: 'scan',
                        post_type: postType,
                        offset: offset,
                        batch_size: batchSize,
                    },
                    success: function(res) {
                        if (res.success) {
                            scannedPosts += res.data.scanned;
                            offset += batchSize;
                            
                            const percent = Math.min((scannedPosts / totalPosts) * 100, 100);
                            $('#progress-fill').css('width', percent + '%');
                            $('#progress-text').text(scannedPosts + ' / ' + totalPosts + ' posts scanned');
                            
                            if (scannedPosts < totalPosts) {
                                scanBatch(postType, batchSize);
                            } else {
                                $('#status-text').text('✓ Complete! ' + scannedPosts + ' posts processed.');
                                scanInProgress = false;
                            }
                        }
                    }
                });
            }
            
            $('#single-scan-form').on('submit', function(e) {
                e.preventDefault();
                const postId = $('[name="post_id"]').val();
                
                $.ajax({
                    url: ajaxurl,
                    type: 'POST',
                    data: {
                        action: 'topic_single_scan',
                        post_id: postId,
                    },
                    success: function(res) {
                        if (res.success) {
                            alert('Post #' + postId + ' scanned. Topics found: ' + res.data.topics.join(', ') + '. Links: ' + res.data.links.length);
                        }
                    }
                });
            });
        });
        </script>
        <?php
    }
    
    public function ajax_bulk_scan() {
        if ( ! current_user_can( 'manage_options' ) ) {
            wp_send_json_error( 'Unauthorized' );
        }
        
        $mode = isset( $_POST['mode'] ) ? sanitize_text_field( $_POST['mode'] ) : 'count';
        $post_type = isset( $_POST['post_type'] ) ? sanitize_text_field( $_POST['post_type'] ) : 'post';
        
        $args = array(
            'post_type' => $post_type,
            'post_status' => 'publish',
            'posts_per_page' => -1,
            'fields' => 'ids',
        );
        
        if ( $mode === 'count' ) {
            $count = count( get_posts( $args ) );
            wp_send_json_success( array( 'total' => $count ) );
        }
        
        if ( $mode === 'scan' ) {
            $offset = isset( $_POST['offset'] ) ? intval( $_POST['offset'] ) : 0;
            $batch_size = isset( $_POST['batch_size'] ) ? intval( $_POST['batch_size'] ) : 10;
            
            $args['offset'] = $offset;
            $args['posts_per_page'] = $batch_size;
            
            $post_ids = get_posts( $args );
            $scanned = 0;
            
            foreach ( $post_ids as $post_id ) {
                $this->scan_and_store_post( $post_id );
                $scanned++;
            }
            
            wp_send_json_success( array( 'scanned' => $scanned ) );
        }
        
        wp_send_json_error( 'Invalid mode' );
    }
    
    public function ajax_single_scan() {
        if ( ! current_user_can( 'manage_options' ) ) {
            wp_send_json_error( 'Unauthorized' );
        }
        
        $post_id = isset( $_POST['post_id'] ) ? intval( $_POST['post_id'] ) : 0;
        
        if ( ! $post_id ) {
            wp_send_json_error( 'No post ID' );
        }
        
        $topics = $this->detect_post_topics( $post_id );
        $links = $this->find_topic_matches( $post_id, $topics );
        
        update_post_meta( $post_id, 'topic_tags', $topics );
        update_post_meta( $post_id, 'reciprocal_links', $links );
        
        wp_send_json_success( array(
            'topics' => $topics,
            'links' => $links,
        ) );
    }
    
    private function scan_and_store_post( $post_id ) {
        $topics = $this->detect_post_topics( $post_id );
        if ( ! empty( $topics ) ) {
            update_post_meta( $post_id, 'topic_tags', $topics );
            
            $links = $this->find_topic_matches( $post_id, $topics );
            if ( ! empty( $links ) ) {
                update_post_meta( $post_id, 'reciprocal_links', $links );
            }
        }
    }
    
    private function detect_post_topics( $post_id ) {
        $post = get_post( $post_id );
        if ( ! $post ) {
            return array();
        }
        
        $text = strtolower( $post->post_title . ' ' . $post->post_content );
        $detected_topics = array();
        
        foreach ( $this->topic_keywords as $topic => $keywords ) {
            $matches = 0;
            foreach ( $keywords as $keyword ) {
                if ( strpos( $text, $keyword ) !== false ) {
                    $matches++;
                }
            }
            
            if ( $matches >= 1 ) {
                $detected_topics[] = $topic;
            }
        }
        
        return array_unique( $detected_topics );
    }
    
    private function find_topic_matches( $post_id, $topics ) {
        if ( empty( $topics ) ) {
            return array();
        }
        
        $matches = array();
        $external_blogs = $this->get_external_blogs();
        
        foreach ( $external_blogs as $blog_key => $blog_data ) {
            $feed_posts = $this->fetch_and_tag_feed( $blog_data['feed'] );
            
            foreach ( $feed_posts as $feed_post ) {
                $feed_topics = $feed_post['topics'];
                $shared_topics = array_intersect( $topics, $feed_topics );
                
                if ( ! empty( $shared_topics ) ) {
                    $matches[] = array(
                        'blog' => $blog_data['name'],
                        'title' => $feed_post['title'],
                        'url' => $feed_post['link'],
                        'topics' => $shared_topics,
                    );
                }
            }
        }
        
        return array_slice( $matches, 0, 10 );
    }
    
    private function fetch_and_tag_feed( $feed_url ) {
        $cache_key = 'topic_feed_' . md5( $feed_url );
        $cached = get_transient( $cache_key );
        
        if ( $cached ) {
            return $cached;
        }
        
        require_once( ABSPATH . 'wp-includes/feed.php' );
        $feed = fetch_feed( $feed_url );
        
        if ( is_wp_error( $feed ) ) {
            return array();
        }
        
        $posts = array();
        $items = $feed->get_items( 0, 50 );
        
        foreach ( $items as $item ) {
            $text = strtolower( $item->get_title() . ' ' . strip_tags( $item->get_description() ) );
            $topics = array();
            
            foreach ( $this->topic_keywords as $topic => $keywords ) {
                foreach ( $keywords as $keyword ) {
                    if ( strpos( $text, $keyword ) !== false ) {
                        $topics[] = $topic;
                        break;
                    }
                }
            }
            
            if ( ! empty( $topics ) ) {
                $posts[] = array(
                    'title' => $item->get_title(),
                    'link' => $item->get_link(),
                    'topics' => array_unique( $topics ),
                );
            }
        }
        
        set_transient( $cache_key, $posts, $this->cache_duration );
        return $posts;
    }
    
    public function inject_reciprocal_links( $content ) {
        if ( ! is_singular( 'post' ) || ! is_main_query() ) {
            return $content;
        }
        
        $post_id = get_the_ID();
        $links = get_post_meta( $post_id, 'reciprocal_links', true );
        
        if ( empty( $links ) ) {
            return $content;
        }
        
        $html = '<div class="reciprocal-links" style="margin-top: 40px; padding: 20px; background: #f9f9f9; border-left: 4px solid #0073aa;">';
        $html .= '<h3 style="margin-top: 0;">Related Content from Our Network</h3>';
        $html .= '<ul style="list-style: none; padding: 0;">';
        
        foreach ( array_slice( $links, 0, 5 ) as $link ) {
            $topics_str = implode( ', ', $link['topics'] );
            $html .= sprintf(
                '<li style="margin-bottom: 12px;"><a href="%s" rel="external" style="color: #0073aa; text-decoration: none;"><strong>%s</strong></a><br/><span style="color: #666; font-size: 0.85em;">%s • %s</span></li>',
                esc_url( $link['url'] ),
                esc_html( $link['title'] ),
                esc_html( $link['blog'] ),
                esc_html( $topics_str )
            );
        }
        
        $html .= '</ul></div>';
        
        return $content . $html;
    }
}

new Topic_Reciprocal_Link_Manager();
?>
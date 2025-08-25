<?php
/*
Plugin Name: Icog Tag Recommender
Description: Recommends tags for posts using an AI backend.
Version: 1.0
Author: Amanuel Ayalew
*/

if ( ! defined( 'ABSPATH' ) ) exit;

// Enqueue JS
function icog_tag_recommender_enqueue_scripts($hook) {
    if ( $hook === 'post.php' || $hook === 'post-new.php' ) {
        wp_enqueue_script(
            'icog-tag-recommender-js',
            plugins_url('assets/js/icog-tag-recommender.js', __FILE__),
            array('jquery'),
            null,
            true
        );
       wp_localize_script('icog-tag-recommender-js', 'IcogTagRecommender', array(
    'ajax_url' => admin_url('admin-ajax.php'),
    'fastapi_url' => 'http://host.docker.internal:8000/recommend/json' 
));

    }
}
add_action('admin_enqueue_scripts', 'icog_tag_recommender_enqueue_scripts');

// Add meta box
function icog_tag_recommender_meta_box() {
    add_meta_box(
        'icog_tag_recommender',
        'AI Tag Recommendation',
        'icog_tag_recommender_meta_box_callback',
        'post',
        'side'
    );
}
add_action('add_meta_boxes', 'icog_tag_recommender_meta_box');

function icog_tag_recommender_meta_box_callback($post) {
    echo '<button id="icog-tag-recommend-btn" type="button">Get AI Tag Recommendation</button>';
    echo '<div id="icog-tag-recommend-result"></div>';
}

// AJAX handler (optional, if you want to proxy requests via WP)
add_action('wp_ajax_icog_tag_recommender', 'icog_tag_recommender_ajax');
function icog_tag_recommender_ajax() {
    // You can forward the request to FastAPI here if you want to hide the endpoint
    wp_send_json_error('Direct FastAPI call recommended via JS.');
}
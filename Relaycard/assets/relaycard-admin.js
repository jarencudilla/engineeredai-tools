/**
 * relaycard-admin.js
 *
 * Handles live preview refresh and style picker UI interactions.
 * Depends on relaycardAdmin.ajaxUrl and relaycardAdmin.nonce (localized).
 */

( function( $ ) {
    'use strict';

    // — Highlight selected style/ratio/font options on click —
    $( '.relaycard-style-picker, .relaycard-ratio-picker, .relaycard-font-picker' ).on( 'change', 'input[type="radio"]', function() {
        $( this ).closest( '.relaycard-style-picker, .relaycard-ratio-picker, .relaycard-font-picker' )
            .find( 'label' )
            .removeClass( 'is-selected' );
        $( this ).closest( 'label' ).addClass( 'is-selected' );
        refreshPreview();
    } );

    // — Update accent hex display on color change —
    $( '#relaycard-accent' ).on( 'input', function() {
        $( '.relaycard-accent-hex' ).text( $( this ).val() );
        refreshPreview();
    } );

    // — Manual refresh button —
    $( '#relaycard-preview-btn' ).on( 'click', refreshPreview );

    // — Initial preview load —
    refreshPreview();

    /**
     * refreshPreview
     * Fires AJAX call to get card HTML with current settings and renders it.
     */
    function refreshPreview() {
        var $frame = $( '#relaycard-preview-frame' );
        $frame.html( '<p style="color:#aaa;text-align:center;padding:2rem 0;">Loading preview...</p>' );

        $.post( relaycardAdmin.ajaxUrl, {
            action: 'relaycard_preview',
            nonce:  relaycardAdmin.nonce,
        }, function( response ) {
            if ( response.success && response.data.html ) {
                $frame.html( response.data.html );
            } else {
                $frame.html( '<p style="color:#aaa;text-align:center;padding:2rem 0;">Preview unavailable.</p>' );
            }
        } );
    }

} )( jQuery );

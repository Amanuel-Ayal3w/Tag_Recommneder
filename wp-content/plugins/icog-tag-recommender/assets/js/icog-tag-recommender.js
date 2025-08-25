jQuery(document).ready(function($) {
    $('#icog-tag-recommend-btn').on('click', function() {
        // Collect post content for Gutenberg/block editor
        let postContent = '';
        if (typeof wp !== 'undefined' && wp.data) {
            postContent = wp.data.select('core/editor').getEditedPostContent();
        } else if ($('#content').length && $('#content').val()) {
            postContent = $('#content').val();
        } else if (typeof tinyMCE !== 'undefined' && tinyMCE.activeEditor) {
            postContent = tinyMCE.activeEditor.getContent();
        }

        let images = [];
        postContent.replace(/<img[^>]+src="([^">]+)"/g, function(_, src) { images.push(src); });
        let videos = [];
        postContent.replace(/<iframe[^>]+src="([^">]+)"/g, function(_, src) { videos.push(src); });

        $('#icog-tag-recommend-result').text('Getting recommendations...');

        // Debug: log what is being sent
        console.log('Sending to FastAPI:', {
            text: postContent,
            images: images,
            videos: videos
        });

        fetch(IcogTagRecommender.fastapi_url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: postContent,
                images: images,
                videos: videos
            })
        })
        .then(response => {
            console.log('FastAPI response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('FastAPI response data:', data);
            if (data.tags) {
                $('#icog-tag-recommend-result').html('<strong>Recommended Tags:</strong> ' + data.tags.join(', '));
            } else {
                $('#icog-tag-recommend-result').text('No tags recommended.');
            }
        })
        .catch((err) => {
            console.error('Error fetching from FastAPI:', err);
            $('#icog-tag-recommend-result').text('Error getting recommendations.');
        });
    });
});
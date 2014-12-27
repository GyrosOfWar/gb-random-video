$(document).ready(function() {
    $.getJSON('/categories').done(function(data) {
        $.each(data, function(shortName, longName) {
            $('#video_type').append('<option value="' + shortName + '">'  + longName + '</option>');
        });
    });
});

$('#go_button').click(function() {
    var category = $('#video_type').val();
    $.get('/random_video/' + category)
        .done(function(url) {
            window.location.href = url;
        });
});

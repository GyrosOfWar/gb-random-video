$(document).ready(function() {
    $.getJSON('/categories').done(function(data) {
        $.each(data, function(shortName, longName) {
            $('#video_type').append('<option value="' + shortName + '">'  + longName + '</option>');
        });
    });
});

$('#go_button').click(function() {
    var category = $('#video_type').val();
    console.log("category = " + category);
    $.getJSON('/random_video/' + category).done(function(url) {
        console.log("url = " + url);
        window.location.href = url;
    });
});

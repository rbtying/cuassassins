$(document).ready(function() {
    $('form select').html($('form select option').sort(function(a,b) {
        return a.text == b.text ? 0 : a.text < b.text ? -1 : 1
    }))
});

$(document).ready(function() {
    $("#file-form").change(function() {
        $("#spinner").show();
        $("#up-file-txt").hide();
        $(this).submit();
    });
});

$(document).ready(function(){
    program_id = get_id('id');
    http('program/' + program_id, 'GET', null, function(response) {
        $("#program_details").html(response['steps']);
    });
});
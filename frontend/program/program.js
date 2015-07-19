$(document).ready(function(){
    $("#new_program").click( function(){
            window.location.href = '/program/new?user=' + get_user_id();
        }
    );

    http('user/' + get_user_id() + '/programs', 'GET', null, function(data){
        buttons = ''
        for (i=0; i<data.length; i++) {
            line = "<input type='submit' value='"
            line += data[i]['name']
            line += "'><br>"
            buttons += line;
        }
    $("#programs").html(buttons);
    });
});

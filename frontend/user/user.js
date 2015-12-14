$(document).ready(function(){
    $("#new_program").click( function(){
            window.location.href = '/program/new?user=' + get_id('user');
        }
    );

    $("#delete").click( function(){
            if (window.confirm("Are you sure you want to delete this user? This CANNOT be undone.")) {
                http('user/' + get_id('user'), 'DELETE', null, function(data) {
                    window.location.href='/';
                });
            }
        }
    );

    http('user/' + get_id('user'), 'GET', null, function(data){
        $("#username").html(data['name']);
    });

    http('program?user=' + get_id('user'), 'GET', null, function(data){
        buttons = ''
        for (i=0; i<data.length; i++) {
            line = "<input type='submit' class='program_button' value='"
            line += data[i]['name'].replace(/'/g, '&#39;')
            line += "'"
            line += "onclick='window.location.href=\"/program/manage/?id=" + data[i]['id'] + "\"'><br>"
            buttons += line;
        }
    if (buttons == '') {
        $("#programs").html("No programs for this user.")
    }
    else {
        $("#programs").html(buttons);
    }
    });
});

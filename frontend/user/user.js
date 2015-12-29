$(document).ready(function(){

    // button to create new programs for the given user
    $("#new_program").click( function(){
        // just takes the user to the new program page
        window.location.href = '/program/new?user=' + get_id('user');
    });

    // button to delete the current user
    $("#delete").click(function(){
        if (window.confirm("Are you sure you want to delete this user? This CANNOT be undone.")) {
            http('user/' + get_id('user'), 'DELETE', null, function(data) {
                // after deleting the user, go back to the homepage
                window.location.href='/';
            });
        }
    });

    // get the user's name so it can be displayed
    http('user/' + get_id('user'), 'GET', null, function(data){
        $("#username").html(data['name']);
    });

    // get a list of programs the user has created, if any, and make buttons for each
    http('program?user=' + get_id('user'), 'GET', null, function(data){
        var buttons = '';
        for (var i=0; i<data.length; i++) {
            var line = "<input type='submit' class='program_button' value='";
            // handle names with single quotes
            line += data[i]['name'].replace(/'/g, '&#39;');
            line += "'";
            line += "onclick='window.location.href=\"/program/manage/?id=" + data[i]['id'] + "\"'><br>";
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

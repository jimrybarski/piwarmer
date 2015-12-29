$(document).ready(function(){
    // user creation button
    $("#create_new_user").click( function()
        {
            // grab the username from the text box
            var name = $("#new_username").val();
            if (name.length > 0) {
                http('user', 'POST', {'name': name}, function(data){
                    // create the new user, empty the text box, and refresh the page to show the new user button
                    $("#new_username").val('');
                    location.reload();
                });
            }
            else {
                // the text box was empty so we can't create a new user
                alert("Please enter a name.")
            }
        }
    );

    // load users and make a button for each of them
    http('user', 'GET', null, function(data){
        var buttons = '';
        for (var i=0; i<data.length; i++) {
            var line = "<input type='submit' onclick='window.location.href=";
            line += '"/user?user=';
            line += data[i]['id'];
            line += '"\' value="';
            line += data[i]['name'];
            line += '"><br>';
            buttons += line;
        }
    if (buttons == '') {
        buttons = 'No users exist yet.'
    }
    $("#users").html(buttons);
    });
});

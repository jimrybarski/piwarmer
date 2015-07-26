$(document).ready(function(){
    $("#create_new_user").click( function()
        {
            name = $("#new_username").val();
            if (name.length > 0) {
                http('user', 'POST', {'name': name}, function(data){
                    $("#new_username").val('');
                    location.reload();
                })
            }
            else {
                alert("Please enter a name.")
            }
        }
    );

    http('user', 'GET', null, function(data){
        buttons = ''
        for (i=0; i<data.length; i++) {
            line = "<input type='submit' onclick='window.location.href="
            line += '"/program?user='
            line += data[i]['id']
            line += '"\' value="'
            line += data[i]['name']
            line += '"><br>'
            buttons += line;
        }
    if (buttons == '') {
        buttons = 'No users exist yet.'
    }
    $("#users").html(buttons);

    });
});

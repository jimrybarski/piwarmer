$(document).ready(function(){
    // user creation button
    $("#create_new_driver").click( function()
        {
            window.location.href = '/driver/new';
        }
    );

    // load users and make a button for each of them
    http('driver', 'GET', null, function(data){
        var buttons = '';
        for (var i=0; i<data.length; i++) {
            var line = "<input type='submit' onclick='window.location.href=";
            line += '"/driver/manage?id=';
            line += data[i]['id'];
            line += '"\' value="';
            line += data[i]['name'];
            line += '"><br>';
            buttons += line;
        }
    if (buttons == '') {
        buttons = 'No drivers exist yet.'
    }
    $("#drivers").html(buttons);
    });
});

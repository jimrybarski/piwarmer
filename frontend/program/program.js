$(document).ready(function(){
    $("#new_program").click( function(){
            window.location.href = '/program/new?user=' + get_id('user');
        }
    );

    http('program?user=' + get_id('user'), 'GET', null, function(data){
        console.log("YUP")
        console.log(data)

        buttons = ''
        for (i=0; i<data.length; i++) {
            line = "<input type='submit' value='"
            line += data[i]['name']
            line += "'"
            line += "onclick='window.location.href=\"/program/manage/?id=" + data[i]['id'] + "\"'><br>"
            buttons += line;
        }
    $("#programs").html(buttons);
    });
});

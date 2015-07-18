$(document).ready(function(){
    var parser = document.createElement('a');
    parser.href = window.location.href;
    user_id = parser.search.replace(/\?user=/, '')

    http('user/' + user_id + '/programs', 'GET', null, function(data){
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

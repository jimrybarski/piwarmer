$(document).ready(function(){
    http("logs", 'GET', null, function(data){
        $("#logs").html(data);
});

$(document).ready(function(){
    // this isn't really complete yet, just gets a list of log filenames
    http("logs", 'GET', null, function(data) {
        var output = "";
        for (var i=0; i<Object.keys(data).length; i++) {
            output += data[i] + "<br>";
       }
       $("#logs").html(output);
   });
});
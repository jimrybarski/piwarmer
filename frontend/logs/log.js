$(document).ready(function(){
   http("logs", 'GET', null, function(data) {

       var output = "";

       for (i=0; i<Object.keys(data).length; i++) {
           output += data[i] + "<br>";
       }

       $("#logs").html(output);
  
   });
});
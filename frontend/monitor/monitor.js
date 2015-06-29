function get(endpoint, func){
    $.ajax({
      type: "GET",
      crossDomain: true,
      url: "http://192.168.10.1/backend/" + endpoint,
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function(data){
        func(data)
      },
      failure: function(data) {
        alert("The API could not be reached.")
      },
    });
}

function post(endpoint, func){
    $.ajax({
      type: "POST",
      crossDomain: true,
      url: "http://192.168.10.1/backend/" + endpoint,
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function(data){
        func(data)
      },
      failure: function(data) {
        alert("Error! Could not stop heater. Please turn off the device power.")
      },
    });
}

function update() {
  get("current", function(data){
    $("#current_temp").html("Temp: " + data.temp)
    $("#current_mode").html("Current Setting: " + data.setting)
    $("#time_left").html("Time remaining: " + data.time_left)
  })
}

$(document).ready(function(){
    $("#stop").click( function()
        {
            post("stop", function(data){
                alert("Program has stopped and the heater is shut down.")
            })
        }
    );
    $("#new_program").click( function()
        {
            post("stop", function(data){
                window.location.replace("http://192.168.10.1/");
            })
        }
    );
    var intervalID = window.setInterval(update, 1000);
});


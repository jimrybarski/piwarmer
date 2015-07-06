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
    $("#current_temperature_setting").html("Current Setting: " + data.setting)
    $("#time_left").html("Time remaining: " + data.time_left)
    var next_steps = "<table><thead class="setting"><tr><th scope="col">Step</th><th>Starts In</th></tr></thead>"
    next_steps += "<tbody><tr><td>" + data.next_steps[0] + "</td><td>Running</td></tr></tbody>"
    for (i=1; i<data.next_steps.length; i++) {
        line = "<tfoot><tr><td>" + data.next_steps[i] + "</td><td>" + data.times_until[i] + "</td></tr></tfoot>"
        next_steps += line
    }
    next_steps += "</table>"
    $("next_steps").html(next_steps)
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

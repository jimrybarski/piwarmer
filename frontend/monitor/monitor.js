function get(endpoint, func){
    $.ajax({
      type: "GET",
      crossDomain: true,
      url: "http://10.42.0.86/api/" + endpoint,
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

function update() {
  get("current", function(data){
    $("#current_temp").html("Temp: " + data.temp)
    $("#current_mode").html("Current Setting: " + data.setting)
    $("#minutes_left").html("Time remaining: " + data.minutes_left)
  })
}

$(document).ready(function(){
    var intervalID = window.setInterval(update, 1000);
});

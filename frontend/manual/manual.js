function get(endpoint, func){
    $.ajax({
      type: "GET",
      crossDomain: true,
      url: "http://10.42.0.86/backend/" + endpoint,
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

function change_temp(amount) {
        var new_temp = parseInt($("#desired_temp").html()) + amount;
        $("#desired_temp").html(new_temp);
    };

function toggle_mode(mode) {
    if (mode == "start") {
        var new_toggle_button = '<button id="start" type="button">Activate Temperature Control</button>';
    }
    if (mode == "stop") {
        var new_toggle_button = '<button id="stop" type="button">Deactivate Temperature Control</button>';
    }
    $("#toggle").html(new_toggle_button);

//    $.ajax({
//      type: "POST",
//      crossDomain: true,
//      url: "http://10.42.0.86/backend/" + mode
//    });

}

function update() {
  get("current", function(data){
    $("#actual_temp").html(data.temp)
  });
}

$(document).ready(function() {
    $(document.body).on('click', '#plus_ten', function() {
        change_temp(10);
    });
    $(document.body).on('click', '#plus_one', function() {
        change_temp(1);
    });
    $(document.body).on('click', '#minus_one', function() {
        change_temp(-1);
    });
    $(document.body).on('click', '#minus_ten', function() {
        change_temp(-10);
    });
    $(document.body).on('click', '#start' ,function() {
        toggle_mode("stop");
    });
    $(document.body).on('click', '#stop' ,function() {
        toggle_mode("start");
    });

    var intervalID = window.setInterval(update, 1000);

});
function update() {
    // Get the latest temperature and data about the program that's running
    http("current", 'GET', null, function(data){
        // Update the most important stats
        $("#current_temp").html("Temp: " + data.temp)
        $("#current_temperature_setting").html("Current Setting: " + data.next_steps[0])
        $("#time_left").html("Time remaining: " + data.time_left)

        // Build up the table of next steps
        var next_steps = "<table><thead class='setting'><tr><th scope='col'>Step</th><th>Starts In</th></tr></thead><tfoot class='setting'>"
        for (i=1; i<Object.keys(data.next_steps).length; i++) {
            line = "<tr><td>" + data.next_steps[i] + "</td><td>" + data.times_until[i] + "</td></tr>"
            next_steps += line
        }
        next_steps += "</tfoot></table>"
        $("#next_steps").html(next_steps)
    });
}

$(document).ready(function(){

    // We want to stop the program, but keep monitoring the temperature.
    $("#stop").click(function()
        {
            http("stop", 'POST', null, function(data){
                alert("Program has stopped and the heater is shut down.")
            });
        }
    );

    // We want to quit and go back to the home page. But we need to turn off the heater and end the program first.
    $("#abort_program").click(function()
        {
            http("stop", 'POST', null, function(data){
                window.location.replace("/");
            });
        }
    );

    // once every second, get updated information about the program and the heater from API
    var intervalID = window.setInterval(update, 1000);
});

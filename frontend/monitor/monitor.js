function mode_to_human_readable_text(program) {
    if (program.mode == "set") {
        return "Set to " + program.temperature + "°C"
    }
    if (program.mode == "linear") {
        return "Linear gradient from " + program.start_temperature + "°C" + " to " + program.end_temperature + "°C"
    }
    if (program.mode == "hold") {
        return "Hold at " + program.temperature + "°C"
    }
}

function duration_to_human_readable(program) {
    if (program.mode == "hold") {
        return "---"
    }
    return program.duration
}


function update() {
    // Get the latest temperature and data about the program that's running
    http("current", 'GET', null, function(data){
        // Update the most important stats
        $("#current_temp").html("Temp: " + data.temp)
        $("#current_step").html("Current Step: " + data.step)

        var show_stop_button = (Object.keys(data.program).length > 0)

//        if (data.time_left == "00:00:01" || data.time_left == "00:00:02") {
//            console.log("Beeping!")
//            beep();
//        }
//        // Build up the table of each program step
        var steps = "<table><thead class='setting'><tr><th>Step</th><th>Duration</th></tr></thead><tfoot class='setting'>"
            for (i=0; i<Object.keys(data.program).length; i++) {
                if (data.step == i) {
                    line = "<tr class='current_step'>"
                }
                else if (data.step > i) {
                    line = "<tr class='completed_step'>"
                }
                else {
                    line = "<tr>"
                }
                line += "<td>" + mode_to_human_readable_text(data.program[i]) + "</td>"
                line += "<td>" + duration_to_human_readable(data.program[i]) + "</td>"
                line += "</tr>"
                steps += line
            }
        steps += "</tfoot></table>"

        $("#steps").html(steps)

        if (show_stop_button) {
            $("#stop").prop('disabled', false);
            $("#stop").val("STOP");
            $("#stop").attr('style', 'background-color: #FF2020; color: #FFFFFF;')
        }
        else {
            $("#stop").prop('disabled', true);
            $("#stop").val("No program running");
            $("#stop").attr('style', 'background-color: #806666; color: #FFFFFF;')
        }
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

    // once half second, get updated information about the program and the heater from API
    var intervalID = window.setInterval(update, 1000);
});

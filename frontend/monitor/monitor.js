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
    return to_hhmmss(program.duration)
}


function display_temperature(temperature) {
    // returns a space if we have no data, otherwise returns the formatted temperature
    if (temperature === undefined || temperature === null) {
        return "---";
    }
    rounded_temp = parseFloat(temperature).toFixed(2);
    // add a space when we have two-digit temperatures, to keep spacing the same as when it's 100°C or higher
    return rounded_temp + "°C"
}

function update() {
    // Get the latest temperature and data about the program that's running
    http("current", 'GET', null, function(data){
        // Update the most important stats
        $("#current_temp").html(display_temperature(data.temp));
        $("#target_temp").html(display_temperature(data.target));
        if (data.program_time_remaining == 0) {
            $("#step_time_remaining").html('---');
            $("#program_time_remaining").html('---');
        }
        else {
            $("#step_time_remaining").html(to_hhmmss(data.step_time_remaining));
            $("#program_time_remaining").html(to_hhmmss(data.program_time_remaining));
        }
        var show_stop_button = (Object.keys(data.program).length > 0);

        // Build up the table of each program step
        if (data.step) {
            // see if we have changed steps since the last check. If so, we should beep.
            var current_step = $("#current_step");
            var previous_step = parseInt(current_step.val());
            if (previous_step != data.step) {
                beep();
            }
            current_step.val(data.step);
            var steps = "<table><thead class='setting'><tr><th>Step</th><th>Duration</th></tr></thead><tfoot class='setting'>";
            for (var i = 1; i <= Object.keys(data.program).length; i++) {
                var line;
                if (data.step == i) {
                    line = "<tr class='current_step'>";
                }
                else if (data.step > i) {
                    line = "<tr class='completed_step'>";
                }
                else {
                    line = "<tr>";
                }
                line += "<td>" + mode_to_human_readable_text(data.program[i]) + "</td>";
                line += "<td>" + duration_to_human_readable(data.program[i]) + "</td>";
                line += "</tr>";
                steps += line;
            }
            steps += "</tfoot></table>";

            $("#steps").html(steps);
        }

        if (show_stop_button) {
            $("#stop")
                .prop('disabled', false)
                .val("STOP")
                .attr('style', 'background-color: #FF2020; color: #FFFFFF;');
        }
        else {
            $("#steps").html('');
            $("#stop")
                .prop('disabled', true)
                .val("No program running")
                .attr('style', 'background-color: #806666; color: #FFFFFF;');
        }
    });
}

$(document).ready(function(){
    // We want to stop the program, but keep monitoring the temperature.
    $("#stop").click(function()
        {
            http("stop", 'POST', null, function(data){
                alert("Program has stopped and the heater is shut down.");
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
    window.setInterval(update, 1000);
});

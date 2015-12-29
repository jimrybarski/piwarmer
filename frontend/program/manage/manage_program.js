function display_step(data) {
    // Converts a step data structure into something human-readable
    if (data['mode'] == 'set') {
        return 'Set to ' + data['temperature'] + '&deg;C for ' + to_hhmmss(data['duration'])
    }
    if (data['mode'] == 'linear') {
        return 'Ramp from ' + data['start_temperature'] + '&deg;C to ' + data['end_temperature'] + '&deg;C over ' + to_hhmmss(data['duration'])
    }
    if (data['mode'] == 'hold') {
        return 'Hold at ' + data['temperature'] + '&deg;C'
    }
}

$(document).ready(function(){
    var program_id = get_id('id');
    var scientist;
    var driver_id;
    http('program/' + program_id, 'GET', null, function(response) {
        scientist = response['scientist'];
        // Set the program name
        $("#program_title").html(response['name']);

        // Set the driver name
        http('driver/' + response['driver'], 'GET', null, function(driver_response){
            driver_id = driver_response['id'];
            $("#driver_name").html("Driver: " + driver_response['name']);
        });

        // Parse the steps and build up the HTML
        var step_data = JSON.parse(response['steps']);
        var step_keys = [];
        for (key in step_data) {
            step_keys.push(key);
        }
        step_keys.sort();
        var steps = "";
        for (var key in step_keys) {
            steps += '<tr><td>' + step_keys[key] + '</td><td>' + display_step(step_data[step_keys[key]]) + '</td></tr>';
        }
        $("#program_details").html(steps);
    });

    // Button to run a program
    $(document.body).on('click', '#run', function() {
        var data = {
                'driver': driver_id,
                'program': program_id
                };
        // This request will validate the data first, set it in the Redis interface, and only then if all went fine
        // will the start signal be set. If anything fails, nothing will happen and an HTTP 400 response will be received.
        http('start', 'POST', data, function(response) {
            // If the program started, go to the monitor page to view it
            window.location.href = '/monitor'
        });
    });

    // Delete this program
    $(document.body).on('click', '#delete', function() {
        if (window.confirm('Are you sure you want to delete this program? This CANNOT be undone.')) {
            http('program/' + program_id, 'DELETE', null, function(response) {
                // go back to the user page after deleting the program
                window.location.href = '/user?user=' + scientist;
            });
        }
    });
});
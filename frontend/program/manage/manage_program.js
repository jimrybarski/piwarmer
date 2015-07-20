function display_step(data) {
    if (data['mode'] == 'set') {
        return 'Set to ' + data['temperature'] + '&deg;C for ' + data['duration'] + ' seconds'
    }
    if (data['mode'] == 'linear') {
        return 'Ramp from ' + data['start_temperature'] + '&deg;C to ' + data['end_temperature'] + '&deg;C over ' + data['duration'] + ' seconds.'
    }
    if (data['mode'] == 'hold') {
        return 'Hold at ' + data['temperature'] + '&deg;C'
    }
    if (data['mode'] == 'repeat') {
        return 'Repeat ' + data['num_repeats'] + ' times'
    }
}

$(document).ready(function(){
    program_id = get_id('id');
    http('program/' + program_id, 'GET', null, function(response) {
        $("#program_title").html(response['name']);
        step_data = JSON.parse(response['steps']);
        step_keys = [];
        steps = "";
        for (var key in step_data) {
            step_keys.push(key);
        }
        step_keys.sort()
        for (var key in step_keys) {
            steps += '<tr><td>' + step_keys[key] + '</td><td>' + display_step(step_data[step_keys[key]]) + '</td></tr>';
        }

        $("#program_details").html(steps);
    });
});
$(document).ready(function(){
    $(document.body).on('click', '#update', function() {
        updated_driver = {'id': driver_id,
                          'name': $('#name').val(),
                          'kp': $('#kp').val(),
                          'ki': $('#ki').val(),
                          'kd': $('#kd').val(),
                          'max_accumulated_error': $('#max_accumulated_error').val(),
                          'min_accumulated_error': $('#min_accumulated_error').val(),
                          'max_power': $('#max_power').val()
                          }
        http('driver/' + driver_id, 'PUT', updated_driver, function(d){
            alert('Driver updated!');
            $('#driver_name').html('Update PID values for ' + $('#name').val());
        });
    });


    // load the driver parameters and display them in text boxes
    var driver_id = get_id('id');
    http('driver/' + driver_id, 'GET', null, function(response) {
        var name = response['name'];
        var kp = response['kp'];
        var ki = response['ki'];
        var kd = response['kd'];
        var max_accumulated_error = response['max_accumulated_error'];
        var min_accumulated_error = response['min_accumulated_error'];
        var max_power = response['max_power'];

        $('#driver_name').html("Update PID values for " + name);
        $('#name').val(name);
        $('#kp').val(kp);
        $('#ki').val(ki);
        $('#kd').val(kd);
        $('#max_accumulated_error').val(max_accumulated_error);
        $('#min_accumulated_error').val(min_accumulated_error);
        $('#max_power').val(max_power);
    });
});

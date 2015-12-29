$(document).ready(function(){
    $(document.body).on('click', '#save', function(){
        new_driver = {'name': $('#name').val(),
                      'kp': $('#kp').val(),
                      'ki': $('#ki').val(),
                      'kd': $('#kd').val(),
                      'max_accumulated_error': $('#max_accumulated_error').val(),
                      'min_accumulated_error': $('#min_accumulated_error').val(),
                      'max_power': $('#max_power').val()
                      }
        http('driver', 'POST', new_driver, function(d){
            alert('Driver created!');
            window.location.href = '/';
        });
    });
});

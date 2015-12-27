function validate_time(time) {
    // either HH:MM:SS, MM:SS, H:MM:SS, or M:SS. Also technically H:M:S but that should parse fine into seconds
    var regex = new RegExp('(\\d{1,2}:)?\\d{1,2}:\\d{2}');
    return regex.test(time);
}

function hhmmss_to_seconds(time) {
    var separated_times = time.split(':');
    var total_seconds = 0;
    if (separated_times.length == 3) {
        // handle hours specially
        hours = parseInt(separated_times.shift(), 10);
        total_seconds += 3600 * hours;
    }
    // now just MM, SS
    minutes = parseInt(separated_times[0], 10);
    seconds = parseInt(separated_times[1], 10);
    if (minutes > 59 || seconds > 59) {
        alert("Invalid time: " + time);
        throw 'invalid time';
    }
    result = total_seconds + (minutes * 60) + seconds;
    if (result == 0) {
        alert("Invalid time: " + time);
        throw 'invalid time';
    }
    return result;
}

function get_new_row(id, mode) {
  var front = get_id_td(id) + get_mode_td(id, mode);
  var back;
  if (mode == "set") {
    back = '<td class="program_step"><input type="text" name="temperature" placeholder="Temperature (&deg;C)"></td><td class="program_step"><input type="text" name="duration" placeholder="Duration (HH:MM:SS)"></td><td class="program_step"></td>';
  }

  if (mode == "linear") {
    back = '<td><input type="text" name="start_temperature" placeholder="Start Temperature (&deg;C)"></td><td><input type="text" name="end_temperature" placeholder="End Temperature (&deg;C)"></td><td><input type="text" name="duration" placeholder="Duration (HH:MM:SS)"></td>;'
  }

  if (mode == "hold") {
    back = '<td class="program_step"><input type="text" name="temperature" placeholder="Temperature (&deg;C)"></td><td class="program_step"></td><td class="program_step"></td>';
  }

  if (mode == "repeat") {
    back = '<td class="program_step"><input type="text" name="num_repeats" placeholder="Number of repeats"></td><td class="program_step"></td><td class="program_step"></td>';
  }

  return front + back;
}

function get_id_td(id) {
  return '<td class="step_id">' + id + '</td>';
}

function get_mode_td(id, mode) {
  return '<td><select id="' + id + '" class="mode" name="mode"><option value="set">Set</option><option value="hold">Hold</option><option value="linear">Linear Gradient</option><option value="repeat">Repeat</option></select></td>';
}

$(document).ready(function(){

  // generate the first row instead of hard coding it in the HTML so we can guarantee consistency
  var first_row = get_new_row(0, "set");
  $("#temperature_settings tr:first").html(first_row);

  // adds additional rows so any number of instructions can be given to the temperature controller
  $(document.body).on('click', '#add_button' ,function() {
    var last_id = parseInt($("#temperature_settings tr:last").find('td:first').html());
    var last_item = $("#" + last_id).val();
    if (last_item != "hold") {
        var new_id = last_id + 1;
        var new_row = '<tr>' + get_new_row(new_id, "set") + '</tr>';
        $("#temperature_settings tr:last").after(new_row);
    } else {
        alert("You can't add any settings after a hold.")
    }
  });

  http('driver', 'GET', null, function(d){
      var options = '<option value="-1">Choose a Driver</option>';
          for (var i=0; i<d.length; i++) {
              options += "<option value='" + d[i]['id'] + "'>" + d[i]['name'] + "</option>";
          }
      $("#driver").empty().append(options);
  });

  // different modes need different inputs, so we change the elements available in the row to accommodate that
  $(document.body).on('change', '.mode' ,function() {
     var new_row = get_new_row(this.id, this.value);
     var id = this.id;
     var mode = this.value;
     // we're currently in the dropdown element. two levels up gives us the entire row
     $(this).parent().parent().html(new_row);
     $("#" + id).val(mode);
  });

  // validate and save the program
  $(document.body).on('click', '#save' ,function() {
    var program = {};
    var row_id = 0;
    $("#settings").serializeArray().map(function(item) {

      if (item.name == "mode") {
        // we're on a new row (i.e. a new instruction)
        row_id++;
        program[row_id] = {"mode": item.value};
      } else {
        if (item.name == "duration") {
            if (!validate_time(item.value)) {
                alert("Invalid time in step " + row_id + ": " + item.value);
                throw 'Invalid time';
            }
        }
          else if (item.name == "temperature") {
            if (!$.isNumeric(item.value)) {
                alert("Invalid temperature in step " + row_id + ": " + item.value);
                throw 'Invalid temperature';
            }
        }
        program[row_id][item.name] = (item.name == "duration" ? hhmmss_to_seconds(item.value) : item.value);
      }
    });

    var errors = [];
    var name = $("#name").val();
    if (name.length == 0) {
        errors.push("You need to enter a name.")
    }
    var driver = $("#driver").val();
    if (driver == "-1") {
        errors.push("You need to choose a driver.")
    }
    var scientist = get_id('user');
    if (scientist === undefined || scientist < 1) {
        errors.push("You somehow have an invalid scientist ID. Go pick a user first.")
    }
    var data = {'steps': JSON.stringify(program),
                'name': name,
                'driver': driver,
                'scientist': scientist};

    // validate program here
    if (errors.length > 0) {
        var message = "Your program cannot be saved! ";
        for (var i=0; i<errors.length; i++) {
            message += " " + errors[i];
        }
        alert(message);
    }
    else {
      http('program', 'POST', data, function(response) {
          window.location.href = '/program/manage/?id=' + response['id'];
      });
    }
  });
});

function get_new_row(id, mode) {
  var front = get_id_td(id) + get_mode_td(id, mode);

  if (mode == "set") {
    var back = '<td><input type="text" name="temperature" placeholder="Temperature (&deg;C)"></td><td><input type="text" name="duration" placeholder="Duration (sec)"></td>';
  };

  if (mode == "linear") {
    var back = '<td><input type="text" name="start_temperature" placeholder="Start Temperature (&deg;C)"></td><td><input type="text" name="end_temperature" placeholder="End Temperature (&deg;C)"></td><td><input type="text" name="duration" placeholder="Duration (sec)"></td>;'
  }

  if (mode == "hold") {
    var back = '<td><input type="text" name="temperature" placeholder="Temperature (&deg;C)"></td>';
  };

  if (mode == "repeat") {
    var back = '<td><input type="text" name="num_repeats" placeholder="Number of repeats"></td>';
  };

  return front + back;
};

function get_id_td(id) {
  return '<td class="step_id">' + id + '</td>';
};

function get_mode_td(id, mode) {
  return '<td><select id="' + id + '" class="mode" name="mode"><option value="set">Set</option><option value="hold">Hold</option><option value="linear">Linear Gradient</option><option value="repeat">Repeat</option></select></td>';
};

$(document).ready(function(){

  // generate the first row instead of hard coding it in the HTML so we can guarantee consistency
  var first_row = get_new_row(1, "set");
  $("#temperature_settings tr:first").html(first_row);

  // adds additional rows so any number of instructions can be given to the temperature controller
  $(document.body).on('click', '#add_button' ,function() {
    var new_id = parseInt($("#temperature_settings tr:last").find('td:first').html()) + 1;
    var new_row = '<tr>' + get_new_row(new_id, "set") + '</tr>';
    $("#temperature_settings tr:last").after(new_row);
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

  // submit form data to the API
  $(document.body).on('click', '#run_program' ,function() {
    var program = {};
    var row_id = 0;
    $("#settings").serializeArray().map(function(item) {
      if (item.name == "mode") {
        // we're on a new row (i.e. a new instruction)
        row_id++;
        program[row_id] = {"mode": item.value};
      } else {
        program[row_id][item.name] = item.value;
      };
    });
  });

    http('driver', 'GET', null, function(d){
        options = '<option>Choose a Driver</option>'
        for (i=0; i<d.length; i++) {
            option = "<option name='" + d[i]['id'] + "'>"
            option += d[i]['name']
            option += "</option>"
            options += option;
        }
        $("#driver").empty().append(options)
    });
});

//$(document).ready(function(){
//    // get all available drivers and put them into the dropdown
//    http('driver', 'GET', null, function(data){
//        options = '<option>Choose a Driver</option>'
//        for (i=0; i<data.length; i++) {
//            option = "<option id='" + data[i]['id'] + "'>"
//            option += data[i]['name']
//            option += "</option>"
//            options += option;
//        }
//        $("#driver").empty().append(options)
//    });
//
//  // generate the first row instead of hard coding it in the HTML so we can guarantee consistency
//  var first_row = get_new_row(1, "set");
//  $("#temperature_settings tr:first").html(first_row);
//
//
//  // adds additional rows so any number of instructions can be given to the temperature controller
//    $(document.body).on('click', '#add_button' ,function() {
//        var new_id = parseInt($("#temperature_settings tr:last").find('td:first').html()) + 1;
//        var new_row = '<tr>' + get_new_row(new_id, "set") + '</tr>';
//        $("#temperature_settings tr:last").after(new_row);
//    });
//
//
//  // different modes need different inputs, so we change the elements available in the row to accommodate that
//  $(document.body).on('change', '.mode' ,function() {
//     var new_row = get_new_row(this.id, this.value);
//     var id = this.id;
//     var mode = this.value;
//     // we're currently in the dropdown element. two levels up gives us the entire row
//     $(this).parent().parent().html(new_row);
//     $("#" + id).val(mode);
//  });
//
//  // submit form data to the API
//  $(document.body).on('click', '#run_program', function() {
//    var program = {};
//    var row_id = 0;
//        $("#settings").serializeArray().map(function(item) {
//            if (item.name == "mode") {
//                // we're on a new row (i.e. a new instruction)
//                row_id++;
//                program[row_id] = {"mode": item.value};
//            } else {
//                program[row_id][item.name] = item.value;
//            };
//        });
//    });
//});

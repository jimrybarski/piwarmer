var API_URL = 'temp.control:8001'

function http(endpoint, verb, func){
    $.ajax({
      type: verb,
      crossDomain: true,
      url: "http://" + API_URL + "/" + endpoint,
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function(data){
          func(data);
      },
      failure: function(data) {
        alert("The API could not be reached.");
      },
    });
}
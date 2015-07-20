var API_URL = 'temp.control:8001'

function get_id(search_term) {
    var regex = new RegExp('\\?' + search_term + '=');
    var parser = document.createElement('a');
    parser.href = window.location.href;
    return parser.search.replace(regex, '');
}

function http(endpoint, verb, d, func){
    $.ajax({
      type: verb,
      crossDomain: true,
      url: "http://" + API_URL + "/" + endpoint,
      contentType: "application/json; charset=utf-8",
      data: JSON.stringify(d),
      dataType: "json",
      success: function(return_data){
          func(return_data);
      },
      failure: function(return_data) {
        alert("The API could not be reached.");
      },
    });
}
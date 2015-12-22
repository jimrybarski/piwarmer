var API_URL = '127.0.0.1:8000/backend'
//var API_URL = '192.168.10.1'

function get_id(search_term) {
    var regex = new RegExp('\\?' + search_term + '=');
    var parser = document.createElement('a');
    parser.href = window.location.href;
    // Take the 'search' part of the URL (the keyword arguments) and get rid of everything except the ID.
    // Then delete the trailing slash in case one is inserted by the browser
    return parser.search.replace(regex, '').replace('/', '');
}

function beep(){
    // lets the user know that a step finished or the program is over
    var audio = new Audio('../smb_coin.wav');
    audio.play();
}

function http(endpoint, verb, d, func){
    console.log("http(" + endpoint + ", " + verb + ") called with data:")
    console.log(d)
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
    if (verb == "POST") {
        return false;
    }
}

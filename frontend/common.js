var API_URL = '192.168.10.1/backend';
//var API_URL = '127.0.0.1:8000/backend';


function get_id(search_term) {
    // extract the id query parameter from a URL
    var regex = new RegExp('\\?' + search_term + '=');
    var parser = document.createElement('a');
    parser.href = window.location.href;
    // Take the 'search' part of the URL (the keyword arguments) and get rid of everything except the ID.
    // Then delete the trailing slash in case one is inserted by the browser
    return parser.search.replace(regex, '').replace('/', '');
}

function beep(){
    // lets the user know that a step finished or was skipped
    var audio = new Audio('../smb_coin.wav');
    audio.play();
}

function to_hhmmss(seconds) {
    // converts an integer representing seconds into MM:SS or HH:MM:SS format
    if (seconds === null || seconds === undefined) {
        return "---";
    }
    seconds = parseInt(seconds, 10);
    var hours = Math.floor(seconds / 3600);
    var minutes = Math.floor((seconds - (hours * 3600)) / 60);
    seconds = seconds - (hours * 3600) - (minutes * 60);
    var result = "";
    // only use HH:MM:SS if total time is greater than 60 minutes
    if (hours) {
        result += hours + ":"
    }
    // only show leading zero in minute column if we have an hour preceding it
    result += ((minutes < 10 && hours) ? "0" + minutes : minutes) + ":" + (seconds < 10 ? "0" + seconds : seconds);
    return result;
}

function http(endpoint, verb, d, func){
    // a generic function to interact with the given API endpoint
    // verb is an HTTP verb.
    // d is the data, which may be null.
    // func is a function to execute using the *return* data as an argument. usually this is an anonymous function.

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
      }
    });
    if (verb == "POST") {
        // necessary for some stupid reason I forget. Don't remove this.
        return false;
    }
}

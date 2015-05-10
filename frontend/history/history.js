function get(func){
    $.ajax({
      type: "GET",
      crossDomain: true,
      url: "http://10.42.0.86/api/history",
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function(data){
        func(data)
      },
      failure: function(data) {
        alert("The API could not be reached.")
      },
    });
}

$(document).ready(function(){
  get(function(data){
    console.log(data);
    $("#history").empty()
    $.each(data, function(k, v){
      $("#history").append('<a href="' + v + '">' + k + '</a><br>');
    });
  });
});

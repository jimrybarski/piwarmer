data = http('user', 'GET', function(data){
    for (i=0; i<data.length; i++) {
        alert(data[i]['name'] + data[i]['id'])
    }
});
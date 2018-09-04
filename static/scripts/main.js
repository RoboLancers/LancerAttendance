$(document).ready(function() {
    /*var nasa_url = 'https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY&hd=True';
    $.ajax({
        url: nasa_url,
        type: 'GET',
        success: function(result){
            var hd_url = result.hdurl;
            console.log(hd_url);
            $('body').css('background', 'url(' + hd_url + ') no-repeat center')
        }
    });*/

    function refreshAt(hours, minutes, seconds) {
        var now = new Date();
        var then = new Date();

        if(now.getHours() > hours ||
           (now.getHours() == hours && now.getMinutes() > minutes) ||
            now.getHours() == hours && now.getMinutes() == minutes && now.getSeconds() >= seconds) {
            then.setDate(now.getDate() + 1);
        }

        then.setHours(hours);
        then.setMinutes(minutes);
        then.setSeconds(seconds);

        var timeout = (then.getTime() - now.getTime());
        setTimeout(function() { window.location.reload(true); }, timeout);
    }

    refreshAt(0, 10, 0);
});
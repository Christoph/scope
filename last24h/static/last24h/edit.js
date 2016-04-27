
  //jQuery(document).ready(function() {
   
  var post, strin;

  jQuery(document).ready(addClickHandlers());


function addClickHandlers() {

// $('.profileedit').click( function() {
//       post = $(this).attr("name"); //+ "=" + $(this).val();
//       console.log(post)
// })

// $('.alertedit').click( function() {
//       post = $(this).attr("name"); //+ "=" + $(this).val();
//             console.log(post)
// })

jQuery('.alertedit').on('click', function(event) {
    event.preventDefault();
    post = $(this).attr("name"); //+ "=" + $(this).val();
    // var input = $( "#searchform" ).serializeArray();
    // var sources = $( "#sources" ).val();
    //console.log(post)
    if (post == 'save') {
    var input = $( "#alertedit" ).serializeArray();
    //console.log(input);
   jQuery.ajax({
    url: "/alert_edit",
    type: "POST",
    data: {"no":input[1].value, "query":input[2].value,"frequency":input[3].value},
       }).done(function(task) {
        //console.log(task);
                  jQuery('.state_alert').html('<p><strong>Changes have been saved.</strong></p>');
              });
    }

  });

jQuery('.profileedit').on('click', function(event) {
    event.preventDefault();
    post = $(this).attr("name"); //+ "=" + $(this).val();
    
    // var input = $( "#searchform" ).serializeArray();
    // var sources = $( "#sources" ).val();
    var input = $( "#profileedit" ).serializeArray();
    
    if (post == 'save_profile') {   
      
   jQuery.ajax({
    url: "/profile_edit",
    type: "POST",
    data: {"first":input[1].value,"last":input[2].value,"username":input[3].value,"email":input[4].value},
       }).done(function(task) {
                  //console.log(task);
                  jQuery('.state_profile').html('<p><strong>Changes have been saved.</strong></p>');
              });
    }

  });

}

 // );}

// This code is a snippet that makes sure the csrf token is somehow passed from the initial view to the ajaxview, since these cannot be passed on by the jquery...
 $(function() {


    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    /*
    The functions below will create a header with csrftoken
    */

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});

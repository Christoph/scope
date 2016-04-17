
  //jQuery(document).ready(function() {
   
  var post, strin;

  jQuery(document).ready(addClickHandlers());



   function start_task(task_id) {
   // pole state of the current task
   var SearchState = function() {
    jQuery.ajax({
     url: "update_state",
     type: "GET",
     data: {"task_id":task_id, "strin":strin}
    }).done(function(task){

     //console.log(task);
     jQuery('.progress-bar').css({'width': task.substr(1,2) + '%'});
      jQuery('.sr-only').html(task.substr(1,2) + '% Complete');
      jQuery('.status').html(task.substring(3,task.length -1));
      //console.log(task);
      if (task == "50")
      {
    window.location.href = "cs=" + strin;}
     else if (task == "500")
      {
        console.log('hey');
    window.location.href = "server_error";}
  //jQuery.ajax({url: , type: "POST",});}

      else {var timer = setTimeout(SearchState,500);}
    // function() {console.log("yay");
    //     }}

      //.substr(3,task.length -1));
     // if (task.current) {
     //  jQuery('#progress').css({'width': task.current + '%'});
     //  jQuery('#progress').html(task.current + '% Complete')
     // } else {
     //  jQuery('.status').html(task.current);
     // };
     
     // create the infinite loop of Ajax calls to check the state
     // of the current task
     //SearchState();
    });
   }
   
   SearchState();
  };//);

// function addClickHandlers() {
//   $("#progress").click( function() { start_task() });
// }


function extractfeeds(input){ 
      var array = [];
      for (var i = input.length-1; i >= 0; i--) {
        array.push(input[i]['value'])
      }
      console.log(array);
      return array;
    }

function addClickHandlers() {

$('.searchform').click( function() {
      post = $(this).attr("name"); //+ "=" + $(this).val();
})
jQuery('#searchform').on('submit', function(event) {
    event.preventDefault();
    console.log("form submitted!")  // sanity check
    $('#csmodal').modal()
    var input = $( "#searchform" ).serializeArray();
    var sources = $( "#sources" ).val();
    console.log(sources);
    console.log(post);
    console.log(user_id);

    if (post == 'search1') {
      console.log(input[1].value);
   jQuery.ajax({
    url: "search_task_term",
    type: "POST",
    data: {"query_text":input[1].value, "user_id":user_id},
    //  success: function(){
    //  jQuery.ajax({
    //   url: "",
    //   context: document.body,
    //   success: function(s, x) {
    //    jQuery(this).html(s);
    //   }
    //  });
    // }
   }).done(function(task) {
    var output = JSON.parse(task);
    strin = output.strin;
    console.log(output);
    if (output.job != 'exists') {return start_task(output.job);}
      else {window.location.href = "cs=" + strin;}
  
          })

      }
  else if (post == 'search2') {
    console.log(input.slice(2,input.length));
    input = input.slice(2,input.length);
    var array = extractfeeds(input);
   jQuery.ajax({
    url: "search_task_feeds",
    type: "POST",
    data: {"feeds":array,"user_id":user_id},



    //  success: function(){
    //  jQuery.ajax({
    //   url: "",
    //   context: document.body,
    //   success: function(s, x) {
    //    jQuery(this).html(s);
    //   }
    //  });
    // }
   }).done(function(task) {
    console.log(task);
   var output = JSON.parse(task);
    strin = output.strin;
    console.log(output);
      if (output.job != 'exists') {return start_task(output.job);}
      else {window.location.href = "cs=" + strin;}
          })
      }



});}

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
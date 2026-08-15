var modal = document.getElementById("modal");
var close = document.getElementById("close");
let unis = []
let current = "";
let dict = {};
$(document).ready(function () {
    $.ajax({
		url: '/request_universities',
		type: 'POST',
		contentType: 'application/json',
		success: function(response){
		    var res = JSON.parse(response);
		    unis = res.unis;
		},
		error: function(xhr, status, error) {
		alert(xhr.responseText);
    }
	});
});
$('#college').on('input', function() {
    const results = document.getElementById("search-results");
    if ($(this).val().trim().length == 0) {
        results.innerHTML = "";
        results.display = "none";
    }
    else {
        let html = "";
        let count = 0;
        for (let x of unis) {
            if (x.toLowerCase().includes($(this).val().trim().toLowerCase())) {
                html += '<div class="result"><p>'+x+'</p></div>';
                count++;
            }
            if (count == 6) {
                break;
            }
        }
        $('#search-results').css("display", "flex");
        results.innerHTML = html;
        $(".result").on('click', function(){
            current = $(this).html().replace("<p>", "").replace("</p>", "");
            $('.header-text').html(current);
            $('#college').val("");
            results.innerHTML = "";
            results.display = "none";
            $('#d-header').html("Delivery to "+current);
            $('#c-header').html("Add a Trip to "+current);
            getajax();
        });
    }
});

close.onclick = function() {
  modal.style.display = "none";
}

window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}

var add = document.querySelectorAll(".add-button");
var addmodal = document.getElementById("add-modal");
var addclose = document.getElementById("add-close");

add.forEach(element => {
    element.onclick = function() {
        const dep = document.getElementById('departure-input');
        const arr = document.getElementById('arrival-input');
        const now = new Date();
        const year = now.getFullYear();
        const month = (now.getMonth() + 1).toString().padStart(2, '0'); // Month is 0-indexed
        const day = now.getDate().toString().padStart(2, '0');
        const hours = now.getHours().toString().padStart(2, '0');
        const minutes = now.getMinutes().toString().padStart(2, '0');
        const formattedDateTime = `${year}-${month}-${day}T${hours}:${minutes}`;
        // Set the default value of the input
        dep.value = formattedDateTime;
        dep.min = formattedDateTime;
        arr.value = formattedDateTime;
        arr.min = formattedDateTime;
      addmodal.style.display = "block";
    }
});



addclose.onclick = function() {
  addmodal.style.display = "none";
}

var conclose = document.getElementById("confirm-close");
conclose.onclick = function() {
  document.getElementById("confirmation-modal").style.display = "none";
}

window.onclick = function(event) {
  if (event.target == modal) {
    addmodal.style.display = "none";
  }
}

function offsetCalculate(){
    var parentTop = $('#search-bar').offset();
    var parentLeft = $('#search-bar').offset();
    $('#search-results').css({
        'top':parentTop.top,
        'left': parentLeft.left
    });
}

var errorclose = document.getElementById("error-close");
errorclose.onclick = function() {
    document.getElementById("error-modal").style.display = "none";
}

function register(uuid) {
    let name = $('#rname-input').val();
    let phone = $('#rphone-input').val();
    let email = $('#remail-input').val();
    valid = true;
    let message = "";
    if (name.trim().length == 0) {
        valid = false;
        message += "Please enter your name.\n"
    }
    if (!/^\d{10}$/.test(phone)) {
        valid = false;
        message += "Please enter a valid 10-digit phone number.\n";
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        valid = false;
        message += "Please enter a valid email.\n"
    }
    if (valid) {
        $.ajax({
    		url: '/register',
    		data: JSON.stringify({"name": name, "phone": phone, "email": email, "parentid": uuid}),
    		type: 'POST',
    		contentType: 'application/json',
    		success: function(response){
    		    var res = JSON.parse(response);
    		    if (res.error !== undefined) {
                    window.location.href = "fromhome.pythonanywhere.com/";
                }
                else {
        		    getajax();
        		    modal.style.display = "none";
        		    $('#email-confirmation').html(email);
        		    document.getElementById("confirmation-modal").style.display = "block";
        		    reset();
                }
    		},
    		error: function(xhr, status, error) {
    		alert(xhr.responseText);
        }
    	});
    }
    else {
        alert(message);
    }
}

function getajax() {
    let zip_code = $('#zip-filter-input').val();
    if (!/^\d{5}(-\d{4})?$/.test(zip_code)) {
        zip_code = "";
    }
    $.ajax({
		url: '/getDeliveries',
		data: JSON.stringify({"uni": current, "zip_code": zip_code, "filter": $('#filter-input').val()}),
		type: 'POST',
		contentType: 'application/json',
		success: function(response){
		    dict = {};
		    res = JSON.parse(response);
		    const table = document.getElementById("d-table");
            let result = '<tr><th>Location</th><th>Date/Time</th><th id="more-row">Register</th></tr>'
            if (res.result.length == 0) {
                $('#fallback-section').css("display", "flex");
                $('.info-section').css("display", "none");
                $('.deliveries').css("display", "none");
            }
            else {
                for (let x of res.result) {
                    result += '<tr id='+x[9]+' class="delivery-row"><td>'+x[0]+'</td><td>'+x[2]+'</td><td class="more-col"><i class="fa-solid fa-chevron-right fa-lg open" style="color: #000000;"></i></td></tr>';
                    dict[x[9]] = x;
                }
                table.innerHTML = result;
                $(".delivery-row").on('click', function(){
                    const uuid = $(this).attr('id');
                    const item = dict[uuid];
                    $("#locationT").html("<td><p>Location</p></td><td><b>"+item[0]+"</b></td>");
                    $("#dropoffT").html("<td><p>Dropoff</p></td><td><b>"+item[1]+"</b></td>");
                    $("#departureT").html("<td><p>Departure</p></td><td><b>"+item[2]+"</b></td>");
                    $("#arrivalT").html("<td><p>EST Arrival</p></td><td><b>"+item[3]+"</b></td>");
                    $("#spotsT").html("<td><p>Spots Open</p></td><td><b>"+(item[4] - item[11])+"</b></td>");
                    $("#nameT").html("<td><p>Name</p></td><td><b>"+item[5]+"</b></td>");
                    $("#phoneT").html("<td><p>Phone</p></td><td><b>"+item[6]+"</b></td>");
                    $("#zipT").html("<td><p>ZIP Code</p></td><td><b>"+item[13]+"</b></td>");
                    $("#register-button").attr("onclick", "register("+uuid+")");
                    document.getElementById("register-button").onclick = function() {
                        register(uuid);
                    }
                    document.getElementById("link").href="/view/"+uuid;
                    modal.style.display = "block";

                });
                $('.info-section').css("display", "none");
                $('#fallback-section').css("display", "none");
                $('.deliveries').css("display", "block");
            }
		},
		error: function(xhr, status, error) {
		alert(xhr.responseText);
    }
	});
}

function start(uni) {
    current = uni;
    getajax();
    $('.header-text').html(current);
    $('#d-header').html("Delivery to "+current);
    $('#c-header').html("Add a Trip to "+current);
}

$(document).ready(function () {
    offsetCalculate();
});
$(window).resize(function(){
    offsetCalculate();
});

function isNumeric(str) {
  if (typeof str != "string") return false
  return !isNaN(str) &&
         !isNaN(parseFloat(str))
}

function createajax() {
    let start = $('#location-input').val();
    let dropoff = $('#dropoff-input').val();
    let departure = $('#departure-input').val();
    let arrival = $('#arrival-input').val();
    let spots = $('#spots-input').val();
    let name = $('#name-input').val();
    let phone = $('#phone-input').val();
    let email = $('#email-input').val().trim();
    let zip = $('#zip-input').val().trim();
    valid = true;
    let message = "";
    if (start.trim().length == 0) {
        valid = false;
        message += "Please enter the start location.\n"
    }
    if (dropoff.trim().length == 0) {
        valid = false;
        message += "Please enter the dropoff location.\n"
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        valid = false;
        message += "Please enter a valid email.\n"
    }
    if (!/^\d{10}$/.test(phone)) {
        valid = false;
        message += "Please enter a valid 10-digit phone number.\n";
    }
    if (spots === "" || !isNumeric(spots) || +spots > 40) {
        valid = false;
        message += "Please enter a valid number of spots open (less than 40).\n";
    }
    const now = new Date();
    if (new Date(departure) < now) {
        valid = false;
        message += "Please enter a valid departure time (in the future).\n"
    }
    if (new Date(arrival) < new Date(departure) || new Date(arrival) < now) {
        valid = false;
        message += "Please enter a valid arrival time (after the departure).\n"
    }
    if (name.trim().length == 0) {
        valid = false;
        message += "Please enter your name.\n"
    }
    if (!/^\d{5}(-\d{4})?$/.test(zip)) {
        valid = false;
        message += "Please enter a valid 5-digit or US ZIP+4 ZIP code.\n"
    }
    if (valid) {
    	$.ajax({
    		url: '/addDelivery',
    		data: JSON.stringify({"start": start, "dropoff": dropoff, "departure": departure, "arrival": arrival,
    		        "spots": spots, "name": name, "phone": phone, "email": email, "uni": current, "zip": zip}),
    		type: 'POST',
    		contentType: 'application/json',
    		success: function(response){
    		    var res = JSON.parse(response);
    		    getajax();
    		    addmodal.style.display = "none";
    		    $('#email-confirmation').html(email);
    		    $('#panic-link').attr('href', '/edit/delivery/'+res.id+'/'+res.secret);
    		    document.getElementById("confirmation-modal").style.display = "block";
    		    reset();
    		},
    		error: function(xhr, status, error) {
    		alert(xhr.responseText);
        }
    	});
    }
    else {
        alert(message);
    }
}

function view(item) {
    $.ajax({
		url: '/getDeliveryDetails',
		data: JSON.stringify({"id": item}),
		type: 'POST',
		contentType: 'application/json',
		success: function(response){
		    var res = JSON.parse(response);
		    if (res.error !== undefined) {
                window.location.href = "fromhome.pythonanywhere.com/";
            }
		    array = res.result;
            $("#locationT").html("<td><p>Location</p></td><td><b>"+array[0]+"</b></td>");
            $("#dropoffT").html("<td><p>Dropoff</p></td><td><b>"+array[1]+"</b></td>");
            $("#departureT").html("<td><p>Departure</p></td><td><b>"+array[2]+"</b></td>");
            $("#arrivalT").html("<td><p>EST Arrival</p></td><td><b>"+array[3]+"</b></td>");
            $("#spotsT").html("<td><p>Spots Open</p></td><td><b>"+(array[4] - array[11])+"</b></td>");
            $("#nameT").html("<td><p>Name</p></td><td><b>"+array[5]+"</b></td>");
            $("#phoneT").html("<td><p>Phone</p></td><td><b>"+array[6]+"</b></td>");
            $("#register-button").attr("onclick", "register("+item+")");
            $('#d-header').html("Delivery to "+array[10]);
            document.getElementById("link").href="/view/"+item;
            modal.style.display = "block";
            document.getElementById("register-button").onclick = function() {
                register(item);
            }
            start(array[10]);
		},
		error: function(xhr, status, error) {
		alert(xhr.responseText);
    }
	});
	getajax();
}

function reset() {
    $('#location-input').val('');
    $('#dropoff-input').val('');
    $('#spots-input').val('');
    $('#name-input').val('');
    $('#phone-input').val('');
    $('#email-input').val('');
    $('#rname-input').val('');
    $('#rphone-input').val('');
    $('#remail-input').val('');
    const dep = document.getElementById('departure-input');
    const arr = document.getElementById('arrival-input');
    const now = new Date();
    const year = now.getFullYear();
    const month = (now.getMonth() + 1).toString().padStart(2, '0'); // Month is 0-indexed
    const day = now.getDate().toString().padStart(2, '0');
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    const formattedDateTime = `${year}-${month}-${day}T${hours}:${minutes}`;
    dep.value = formattedDateTime;
    dep.min = formattedDateTime;
    arr.value = formattedDateTime;
    arr.min = formattedDateTime;
}

function clearfilters() {
    $('#zip-filter-input').val('');
    $('#filter-input').val(10);
    getajax();
}

$('#apply-filters').click(function() {
    valid = true;
    message = "";
    let zip = $('#zip-filter-input').val();
    if (!/^\d{5}(-\d{4})?$/.test(zip)) {
        valid = false;
        message += "Please enter a valid 5-digit or US ZIP+4 ZIP code.\n"
    }
    let filter = $('#filter-input').val();
    if (filter === "" || !isNumeric(filter) || +filter < 10) {
        valid = false;
        message += "Please enter a valid filter (more than 10 miles).\n";
    }
    if (valid) {
        document.getElementById("zip-modal").style.display = "none";
        getajax();
    }
    else {
        alert(message);
    }
});


$('#create-button').click(function() {
    createajax();
});

$('.location').click(function() {
    document.getElementById("zip-modal").style.display = "flex";
});

$('#clear-filters').click(function() {
    document.getElementById("zip-modal").style.display = "none";
    clearfilters();
});

$('#zip-close').click(function() {
    document.getElementById("zip-modal").style.display = "none";
});
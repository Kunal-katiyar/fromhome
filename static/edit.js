let current = "";
let type = "";
let parentid = "";

function set_time(val, id) {
    const mysqlDatetimeString = val; // Example MySQL DATETIME
    const jsDate = new Date(mysqlDatetimeString.replace(" ", "T"));

    const year = jsDate.getFullYear();
    const month = (jsDate.getMonth() + 1).toString().padStart(2, '0');
    const day = jsDate.getDate().toString().padStart(2, '0');
    const hours = jsDate.getHours().toString().padStart(2, '0');
    const minutes = jsDate.getMinutes().toString().padStart(2, '0');

    const htmlDatetimeLocalString = `${year}-${month}-${day}T${hours}:${minutes}`;
    document.getElementById(id).value = htmlDatetimeLocalString;
}

function getajax_del(val) {
    $(".header").html("Delivery Information");
    current = val;
    type = "delivery";
    $.ajax({
		url: '/getDeliveryDetails',
		data: JSON.stringify({"id": current}),
		type: 'POST',
		contentType: 'application/json',
		success: function(response){
		    res = JSON.parse(response);
		    if (res.error !== undefined) {
                window.location.href = "fromhome.pythonanywhere.com/";
            }
            else {
    		    const item = res.result;
                $("#location-input").val(item[0]);
                $("#dropoff-input").val(item[1]);
                set_time(item[2], "departure-input");
                set_time(item[3], "arrival-input");
                $("#spots-input").val(item[4]);
                $("#name-input").val(item[5]);
                $("#phone-input").val(item[6]);
                $("#email-input").val(item[7]);
                $("#zip-input").val(item[13]);
                parentid = current;
            }
		},
		error: function(xhr, status, error) {
		alert(xhr.responseText);
    }
	});
}

function getajax_res(val) {
    $(".header").html("Reservation Information");
    current = val;
    type = "reservation";
    $.ajax({
		url: '/getDeliveryDetails/res',
		data: JSON.stringify({"id": current}),
		type: 'POST',
		contentType: 'application/json',
		success: function(response){
		    res = JSON.parse(response);
		    if (res.error !== undefined) {
                window.location.href = "fromhome.pythonanywhere.com/";
            }
            else {
    		    const item = res.result;
                $("#name-input").val(item[1]);
                $("#phone-input").val(item[3]);
                $("#email-input").val(item[2]);
                $(".remove").hide();
                parentid = item[4];
            }
		},
		error: function(xhr, status, error) {
		alert(xhr.responseText);
    }
	});
}

function remove() {
    $.ajax({
		url: '/removelogic',
		data: JSON.stringify({"id": current, "type": type}),
		type: 'POST',
		contentType: 'application/json',
		success: function(response){
		    res = JSON.parse(response);
		    if (res.error !== undefined) {
                window.location.href = "fromhome.pythonanywhere.com/";
            } else {
    		    $(".edit-section").html(`
    		    <p>Your submission has succesfully been deleted! If it was a delivery, everyone who signed up will recieve a notice; otherwise, just you will. \n
    		    Once again, thank you for using FromHome! (This link will stop working, you will need to head back to the homepage.)</p>
    		    `);
            }
		},
		error: function(xhr, status, error) {
		alert(xhr.responseText);
        }
    });
}

var trash = document.getElementById("trash-button");
trash.onclick = function() {
  let text = "Are you sure you want to delete this?";
  if (confirm(text) == true) {
    remove();
  }
}

function edit() {
    const validity = validityCheck();
    if (validity[0]) {
        let data = {};
        if (type === "reservation") {
            data = {"id": current, "type": type, "name": $("#name-input").val(), "phone": $("#phone-input").val(), "email": $("#email-input").val()};
        }
        else {
            data = {"id": current,
                "type": type,
                "name": $("#name-input").val(),
                "phone": $("#phone-input").val(),
                "email": $("#email-input").val(),
                "location": $("#location-input").val(),
                "dropoff": $("#dropoff-input").val(),
                "departure": $("#departure-input").val(),
                "arrival": $("#arrival-input").val(),
                "spots": $("#spots-input").val(),
                "zip": $("#zip-input").val()};
        }
        $.ajax({
    		url: '/editlogic',
    		data: JSON.stringify(data),
    		type: 'POST',
    		contentType: 'application/json',
    		success: function(response){
    		    res = JSON.parse(response);
    		    if (res.error !== undefined) {
                    window.location.href = "https://fromhome.pythonanywhere.com/";
                }
    		    let final = `<p>Your submission has succesfully been edited! If it was a delivery, everyone who signed up will recieve a notice; otherwise, just you will. \n
    		    Once again, thank you for using FromHome!`
    		    let link = `"/edit/`+type+`/`+parentid+`/`+res.result+`"`;

    		    if (res.result != "No new key") {
    		        final += `(Since your email was changed, this link will not work anymore: use <a href="/edit/`+type+`/`+parentid+`/`+res.result+`">this link</a>)`;
    		    }
    		    final += "</p>";
    		    $(".edit-section").html(final);
    		},
    		error: function(xhr, status, error) {
    		alert(xhr.responseText);
            }
        });
    } else {
        alert(validity[1]);
    }
}

var editbutton = document.getElementById("edit-button");
editbutton.onclick = function() {
  let text = "Are you sure you want to make these edits?";
  if (confirm(text) == true) {
    edit();
  }
}

function isNumeric(str) {
  if (typeof str != "string") return false
  return !isNaN(str) &&
         !isNaN(parseFloat(str))
}

function validityCheck() {
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
    if (type === "delivery") {
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
        let taken = 0;
        $.ajax({
    		url: '/gettaken',
    		data: JSON.stringify({'id': current}),
    		type: 'POST',
    		contentType: 'application/json',
    		success: function(response){
    		    res = JSON.parse(response);
    		    if (res.error !== undefined) {
                    window.location.href = "fromhome.pythonanywhere.com/";
                }
    		    taken = res.taken;
    		},
    		error: function(xhr, status, error) {
    		alert(xhr.responseText);
            }
        });
        if (spots === "" || !isNumeric(spots) || +spots > 40 || +spots < taken) {
            valid = false;
            message += "Please enter a valid number of spots open (less than 40); must be more than the current amount taken ("+taken+").\n";
        }
        if (new Date(arrival) < new Date(departure)) {
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
    } else {
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            valid = false;
            message += "Please enter a valid email.\n"
        }
        if (!/^\d{10}$/.test(phone)) {
            valid = false;
            message += "Please enter a valid 10-digit phone number.\n";
        }
        if (name.trim().length == 0) {
            valid = false;
            message += "Please enter your name.\n"
        }
    }
    return [valid, message];
}


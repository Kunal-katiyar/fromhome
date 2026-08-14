from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib, ssl
import os
from dotenv import load_dotenv

sender_email = os.getenv("SENDER_EMAIL")
sender_password = os.getenv("SENDER_PASSWORD")
context = ssl.create_default_context()


header = """<html>
<link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css"/>
<style>
    .text {
        font-family: "Lato", serif;
        color: black;
        background-color: white;
        padding: 20px;
    }
    .text h1 {
        text-align: center;
        font-size: 27px;
        font-weight: 500;
    }
    .text p {
        text-align: center;
        font-size: 18px;
        font-weight: 400;
    }
    .text a {
        color: black !important;
    }

  .footer {
    font-family: "Lato", serif;
    width: 100%;
    background-color: #3A3A3A;
    color: white;
    padding: 40px 40px;
    margin-top: 50px;

    a:hover {
      text-decoration: underline;
    }
  }

  .footer h2 {
    font-family: "Playfair Display", serif !important;
    font-weight: 400;
    font-size: 26px;
    font-style: italic;
  }

  .footer p, .footer a {
    font-weight: 400;
    font-size: 20px;
    color: white !important;
    text-align: left;
  }

  .arrow-button {
    margin: auto;
    width: fit-content;
    height: 50px;
    padding: 15px 30px;
    border-radius: 30px;
    /* background-color: whatever */
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 10px;
    transition: all .3s ease;
    background-color: #B9EAAC;
    border: 1px solid black;
  }

  .arrow-button p {
    font-family: 'Inter', sans-serif;
    font-size: 20px;
    font-weight: 400;
    color: black;
    text-decoration: none;
  }

  .arrow-button i {
    color: black;
    transition: all .3s ease;
    height: fit-content;
    width: fit-content;
  }

  .arrow-button:hover {
    transform: scale(1.03);
  }

  .arrow-button:hover > .fa-chevron-right {
    transform: translateX(4px);
  }

  .content-table {
  font-family: "Lato", serif;
  width: 100%;
  padding: 15px;
}

.content-table tr:hover {
  background-color: #dddddd !important;
}

.content-table td, .content-table th {
  border: 1px solid #dddddd;
  text-align: left;
  height: 50px;
  padding-left: 10px;
  padding-right: 7px;
  text-wrap: wrap;
  width: 50%;
}

</style>
  <body>"""


ending = """
<section class="footer">
      <h2>FromHome</h2>
      <p><a>Contact Us</a></p>
    </section>
  </body>
  <script>
     document.getElementById("link").onclick = function (event){
        window.location.href = "https://fromhome.pythonanywhere.com";
     }
  </script>
</html>
"""

def verifyEmail(receiver_email, id, secret):
    message = MIMEMultipart("alternative")
    message["Subject"] = "FromHome Delivery Verification"
    message["From"] = f"FromHome <{sender_email}>"
    message["To"] = receiver_email
    text = """\
    Save this email for future use! If you need to cancel or modify any information; just visit
    fromhome.pythonanywhere.com/edit/delivery/"""+id+"""/"""+secret+"""
    Thank you so much for using FromHome!"""
    html = header + """
    <section class="text">
      <h1>Delivery Confirmation</h1>
      <p>This is simply a delivery verification email. If you did not create a delivery on the FromHome system, you can
      delete the delivery from the link below.
      If this was you, please click on <a href="https://fromhome.pythonanywhere.com/view/"""+id+"""">this link</a>.</p>
      <p>Thank you so much for using FromHome!</p>
      <a href="https://fromhome.pythonanywhere.com">
        <button class="arrow-button" id="link">
            <p>Explore</p><i class="fa-solid fa-chevron-right fa-2x"></i>
        </button>
      </a>
    </section>
    """ + ending
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context)
        server.login(sender_email, sender_password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

def addEmail(receiver_email, id, secret):
    message = MIMEMultipart("alternative")
    message["Subject"] = "FromHome Delivery Confirmation"
    message["From"] = f"FromHome <{sender_email}>"
    message["To"] = receiver_email
    text = """\
    Save this email for future use! If you need to cancel or modify any information; just visit
    fromhome.pythonanywhere.com/edit/delivery/"""+id+"""/"""+secret+"""
    Thank you so much for using FromHome!"""
    html = header + """
    <section class="text">
      <h1>Delivery Confirmation</h1>
      <p>This email is simply to verify that you have inputted the right email into the FromHome system. If this is not you,
       please click on the below link and click the delete button, or reply to this email.</p>
      <p>Save this email for future use! If you need to cancel or modify any information, just click on
      <a href="https://fromhome.pythonanywhere.com/edit/delivery/"""+id+"""/"""+secret+"""">this link</a>.</p>
      <p>If you want to view or share your delivery with others, click on
      <a href="https://fromhome.pythonanywhere.com/view/"""+id+"""">this link</a>.</p>
      <p>Thank you so much for using FromHome!</p>
      <a href="https://fromhome.pythonanywhere.com">
        <button class="arrow-button" id="link">
            <p>Explore</p><i class="fa-solid fa-chevron-right fa-2x"></i>
        </button>
      </a>
    </section>
    """ + ending
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context)
        server.login(sender_email, sender_password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

def addRegister(receiver_email, self, parent):
    message = MIMEMultipart("alternative")
    message["Subject"] = "FromHome Reservation Confirmation"
    message["From"] = f"FromHome <{sender_email}>"
    message["To"] = receiver_email
    text = """\
    Save this email for future use! If you need to cancel or modify any information; just visit
    fromhome.pythonanywhere.com/edit/reservation/"""+parent+"""/"""+self+"""
    Thank you so much for using FromHome!"""
    html = header + """
    <section class="text">
      <h1>Reservation Confirmation</h1>
      <p>This email is simply to verify that you have inputted the right email into the FromHome system. If this is not you,
       please click on the below link and click the delete button, or reply to this email.</p>
      <p>Save this email for future use! If you need to cancel or modify any information, just click on
      <a href="https://fromhome.pythonanywhere.com/edit/reservation/"""+parent+"""/"""+self+"""">this link</a>.</p>
      <p>If you want to view the full delivery, click on
      <a href="https://fromhome.pythonanywhere.com/view/"""+parent+"""">this link</a>.</p>
      <p>Thank you so much for using FromHome!</p>
      <a href="https://fromhome.pythonanywhere.com">
        <button class="arrow-button" id="link">
            <p>Explore</p><i class="fa-solid fa-chevron-right fa-2x"></i>
        </button>
      </a>
    </section>
    """ + ending
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context)
        server.login(sender_email, sender_password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

def removeEmail(receiver_email, item):
    message = MIMEMultipart("alternative")
    message["Subject"] = "Delivery Delete Confirmation"
    message["From"] = f"FromHome <{sender_email}>"
    message["To"] = receiver_email
    text = """\
    This email is to confirm that your delivery to """+item[10]+""" has been deleted. If you had never created one, this may be someone accidentally registering one under your email
    and deleting it, in which case you should have recieved an email regarding its creation. Don't worry: all people who signed up have been notified as well. Thank you so much for using FromHome!"""
    html = header + """
    <section class="text">
      <h1>Delivery Removal</h1>
      <p>This email is to confirm that your delivery to """+item[10]+""" has been deleted. If you had never created one, this may be someone accidentally registering one under your email
      and deleting it, in which case you should have recieved an email regarding its creation. Don't worry: all people who signed up have been notified as well.</p>
      <p>Thank you so much for using FromHome!</p>
      <a href="https://fromhome.pythonanywhere.com">
        <button class="arrow-button" id="link">
            <p>Explore</p><i class="fa-solid fa-chevron-right fa-2x"></i>
        </button>
      </a>
    </section>
    """ + ending
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context)
        server.login(sender_email, sender_password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

def removeEmailIndiv(receiver_email, item):
    message = MIMEMultipart("alternative")
    message["Subject"] = "Delivery Deleted Notice"
    message["From"] = f"FromHome <{sender_email}>"
    message["To"] = receiver_email
    text = """\
    This email is to notify that your delivery to """+item[10]+""" has been deleted by its creator. We're sorry for any inconvenience that may be caused as a result. If you need
    to find a new one, simply head to fromhome.pythonanywhere.com to find a new one. Thank you so much for using FromHome!"""
    html = header + """
    <section class="text">
      <h1>Delivery Removal</h1>
      <p>This email is to notify that your delivery to """+item[10]+""" has been deleted by its creator. We're sorry for any inconvenience that may be caused as a result.</p>
      <p>Thank you so much for using FromHome!</p>
      <p>Need to find a new delivery? Click on the button below!</p>
      <a href="https://fromhome.pythonanywhere.com">
        <button class="arrow-button" id="link">
            <p>Explore</p><i class="fa-solid fa-chevron-right fa-2x"></i>
        </button>
      </a>
    </section>
    """ + ending
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context)
        server.login(sender_email, sender_password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

def indivRemove(receiver_email, item):
    message = MIMEMultipart("alternative")
    message["Subject"] = "Reservation Delete Confirmation"
    message["From"] = f"FromHome <{sender_email}>"
    message["To"] = receiver_email
    text = """\
    This email is to confirm that your reservation to """+item[10]+""" has been deleted. If you had never created one, this may be someone accidentally registering one under your email
    and deleting it, in which case you should have recieved an email regarding its creation. Thank you so much for using FromHome!"""
    html = header + """
    <section class="text">
      <h1>Reservation Deletion</h1>
      <p>This email is to confirm that your reservation to """+item[10]+""" has been deleted. If you had never created one, this may be someone accidentally registering one under your email
      and deleting it, in which case you should have recieved an email regarding its creation.</p>
      <p>Thank you so much for using FromHome!</p>
      <a href="https://fromhome.pythonanywhere.com">
        <button class="arrow-button" id="link">
            <p>Explore</p><i class="fa-solid fa-chevron-right fa-2x"></i>
        </button>
      </a>
    </section>
    """ + ending
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context)
        server.login(sender_email, sender_password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

def editEmail(receiver_email, item):
    message = MIMEMultipart("alternative")
    message["Subject"] = "Your Delivery has been Edited"
    message["From"] = f"FromHome <{sender_email}>"
    message["To"] = receiver_email
    text = """\
    This email is to confirm that your delivery to """+item[10]+""" has been edited. Don't worry: all people who signed up have been notified as well. Thank you so much for using FromHome!"""
    html = header + """
    <section class="text">
      <h1>Delivery Edit</h1>
      <p>This email is to confirm that your reservation to """+item[10]+""" has been deleted. Here are the new details:</p>
      <table class="content-table">
          <tr id="locationT"><td><p>Start Location</p></td><td><b>"""+item[0]+"""</b></td></tr>
          <tr id="dropoffT"><td><p>Dropoff</p></td><td><b>"""+item[1]+"""</b></td></tr>
          <tr id="departureT"><td><p>Departure</p></td><td><b>"""+item[2].strftime("%Y-%m-%d %H:%M:%S")+"""</b></td></tr>
          <tr id="arrivalT"><td><p>EST Arrival</p></td><td><b>"""+item[3].strftime("%Y-%m-%d %H:%M:%S")+"""</b></td></tr>
          <tr id="spotsT"><td><p>Spots Open</p></td><td><b>"""+str((item[4] - item[11]))+"""</b></td></tr>
          <tr id="nameT"><td><p>Name</p></td><td><b>"""+item[5]+"""</b></td></tr>
          <tr id="phoneT"><td><p>Phone</p></td><td><b>"""+str(item[6])+"""</b></td></tr>
          <tr id="emailT"><td><p>Email</p></td><td><b>"""+item[7]+"""</b></td></tr>
          <tr id="zipT"><td><p>ZIP Code</p></td><td><b>"""+str(item[13])+"""</b></td></tr>
      </table>
      <p>If you need to edit it again, head over to <a href="https://fromhome.pythonanywhere.com/edit/delivery/"""+item[9]+"""/"""+item[12]+"""">this link</a>.
      If your email was changed, this link will be different than previous ones.</p>
      <p>Thank you so much for using FromHome!</p>
      <a href="https://fromhome.pythonanywhere.com">
        <button class="arrow-button" id="link">
            <p>Explore</p><i class="fa-solid fa-chevron-right fa-2x"></i>
        </button>
      </a>
    </section>
    """ + ending
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context)
        server.login(sender_email, sender_password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

def editEmailIndiv(receiver_email, item, indiv):
    message = MIMEMultipart("alternative")
    message["Subject"] = "Your Delivery has been Edited"
    message["From"] = f"FromHome <{sender_email}>"
    message["To"] = receiver_email
    text = """\
    This email is to notify that the delivery to """+item[10]+""" you signed up for has been edited. If you want to see the new details, go to
    fromhome.pythonanywhere.com/view/"""+item[9]+""". Thank you so much for using FromHome!"""
    html = header + """
    <section class="text">
      <h1>Delivery Edit</h1>
      <p>This email is to confirm that the delivery to """+item[10]+""" you signed up to has been edited. Here are the new details:</p>
        <table class="content-table">
          <tr id="locationT"><td><p>Start Location</p></td><td><b>"""+item[0]+"""</b></td></tr>
          <tr id="dropoffT"><td><p>Dropoff</p></td><td><b>"""+item[1]+"""</b></td></tr>
          <tr id="departureT"><td><p>Departure</p></td><td><b>"""+item[2].strftime("%Y-%m-%d %H:%M:%S")+"""</b></td></tr>
          <tr id="arrivalT"><td><p>EST Arrival</p></td><td><b>"""+item[3].strftime("%Y-%m-%d %H:%M:%S")+"""</b></td></tr>
          <tr id="spotsT"><td><p>Spots Open</p></td><td><b>"""+str((item[4] - item[11]))+"""</b></td></tr>
          <tr id="nameT"><td><p>Name</p></td><td><b>"""+item[5]+"""</b></td></tr>
          <tr id="phoneT"><td><p>Phone</p></td><td><b>"""+str(item[6])+"""</b></td></tr>
          <tr id="emailT"><td><p>Email</p></td><td><b>"""+item[7]+"""</b></td></tr>
          <tr id="zipT"><td><p>ZIP Code</p></td><td><b>"""+str(item[13])+"""</b></td></tr>
      </table>
      <p>Here is the <a href="https://fromhome.pythonanywhere.com/view/"""+item[9]+"""">link</a> to the full delivery.</p>
      <p>If you need to cancel due to these circumstances, click on
      <a href="https://fromhome.pythonanywhere.com/edit/reservation/"""+item[9]+"""/"""+indiv+"""">this link</a>.</p>
      <p>Thank you so much for using FromHome!</p>
      <a href="https://fromhome.pythonanywhere.com">
        <button class="arrow-button" id="link">
            <p>Explore</p><i class="fa-solid fa-chevron-right fa-2x"></i>
        </button>
      </a>
    </section>
    """ + ending
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context)
        server.login(sender_email, sender_password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

def editReservationEmail(receiver_email, item, uni):
    message = MIMEMultipart("alternative")
    message["Subject"] = "Your Reservation has been Edited"
    message["From"] = f"FromHome <{sender_email}>"
    message["To"] = receiver_email
    text = """\
    This email is to notify that the reservation to """+uni+""" you signed up for has been edited. If you want to see the new details, go to
    fromhome.pythonanywhere.com/edit/reservation/"""+item[4]+"""/"""+item[0]+""". Thank you so much for using FromHome!"""
    html = header + """
    <section class="text">
      <h1>Reservation Edit</h1>
      <p>This email is to confirm that the delivery to """+uni+""" you signed up to has been edited. Here are the new details:</p>
      <table class="content-table">
          <tr id="nameT"><td><p>Name</p></td><td><b>"""+item[1]+"""</b></td></tr>
          <tr id="phoneT"><td><p>Phone</p></td><td><b>"""+item[3]+"""</b></td></tr>
          <tr id="emailT"><td><p>Email</p></td><td><b>"""+item[2]+"""</b></td></tr>
      </table>
      <p>If you need to edit again, click on
      <a href="https://fromhome.pythonanywhere.com/edit/reservation/"""+item[4]+"""/"""+item[0]+"""">this link</a>. If your email was changed, this link will
      be different than previous ones.</p>
      <p>Thank you so much for using FromHome!</p>
      <a href="https://fromhome.pythonanywhere.com">
        <button class="arrow-button" id="link">
            <p>Explore</p><i class="fa-solid fa-chevron-right fa-2x"></i>
        </button>
      </a>
    </section>
    """ + ending
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context)
        server.login(sender_email, sender_password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

from flask import Flask, render_template, request, json, session, redirect
import ssl
import mysql.connector
import uuid
from flask_sqlalchemy import SQLAlchemy
import pgeocode
import csv
from EmailSender import EmailSender
import os
from dotenv import load_dotenv

ES = EmailSender()
load_dotenv()

distance = pgeocode.Nominatim('US')
dist = pgeocode.GeoDistance('US')

uni_names = []
uni_links = []
with open('/home/fromhome/mysite/static/us_universities.csv', 'r') as file:
    reader = csv.reader(file)
    header = next(reader)
    column_index = header.index('name')
    link_index = header.index('url')
    for row in reader:
        if row:
            uni_names.append(row[column_index])
            uni_links.append(row[link_index])


db = mysql.connector.connect(
  host=os.getenv("SQL_HOST"),
  user=os.getenv("SQL_USER"),
  password=os.getenv("SQL_PASSWORD"),
  database=os.getenv("SQL_DATABASE")
)

cursor = db.cursor(buffered = True)
#DELIVERIES: 0start, 1end, 2depart, 3reach, 4spots, 5name, 6phone, 7email, 8people, 9uuid, 10uni, 11taken, 12secret_key, 13zip_code
#INDIVIDUALS: 0id_num, 1name, 2email, 3phone, 4parentid
deliveries = int(os.getenv("NUM_DELIVERIES"))

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRETKEY")
app.config['SQLALCHEMY_POOL_RECYCLE'] = 270

sqldb = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_size' : 100, 'pool_recycle' : 280}
sqldb.init_app(app)

@app.route('/')
def homepage():
    db.ping(reconnect=True, attempts=1, delay=0)
    auto_clear()
    uni = ""
    if session.get('uni') is not None:
        uni = session['uni']

    if session.get('error') is not None:
        error = session['error']
    else:
        error = False
    session['error'] = False
    return render_template("index.html", uni = uni, error = error)

@app.route('/request_universities', methods=["POST"])
def getUnis():
    return json.dumps({'status':'OK', 'unis': uni_names, 'links': uni_links})

@app.route('/about')
def about():
    db.ping(reconnect=True, attempts=1, delay=0)
    auto_clear()
    return render_template("about.html", number = deliveries)

@app.route('/addDelivery', methods=["POST"])
def addDelivery():
    global deliveries
    db.ping(reconnect=True, attempts=1, delay=0)
    data = request.get_json()
    id, secret = addDeliv(data)
    deliveries += 1;
    return json.dumps({'status':'OK', 'id': id, 'secret': secret})

@app.route('/getDeliveries', methods=["POST"])
def getDelivery():
    auto_clear()
    data = request.get_json()
    if data['zip_code'] != "":
        results = getDelivNarrow(data['uni'], data['zip_code'], data['filter'])
    else:
        results = getDeliv(data['uni'])
    session['uni'] = data['uni']
    return json.dumps({'status':'OK', 'result': results})

@app.route('/register', methods=["POST"])
def register():
    data = request.get_json()
    result = indivDeliv(data)
    if result == False:
        session['error'] = True
        print("---------- error found")
        return json.dumps({'status': 'OK', 'error': True})
    return json.dumps({'status':'OK'})

@app.route('/edit/delivery/<string:id>/<string:secret>')
def editdelivery(id, secret):
    db.ping(reconnect=True, attempts=1, delay=0)
    auto_clear()
    result = getByIDProtected(id, secret)
    if result == "Not found":
        session['error'] = True
        return redirect('/')
    else:
        return render_template("edit.html", edit = id, type = "delivery")

@app.route('/view/<string:id>')
def viewdelivery(id):
    db.ping(reconnect=True, attempts=1, delay=0)
    auto_clear()
    result = getByID(id)
    if result == "Not found":
        session['error'] = True
        return redirect('/')
    else:
        return render_template("index.html", view = str(result[1]))

@app.route('/getDeliveryDetails', methods=["POST"])
def ajaxIndiv():
    db.ping(reconnect=True, attempts=1, delay=0)
    data = request.get_json()
    result = getByID(data['id'])[0]
    if result == "Not found":
        session['error'] = True
        return json.dumps({'status': 'OK', 'error': True})
    return json.dumps({'status': 'OK', 'result': result})

@app.route('/getDeliveryDetails/res', methods=["POST"])
def ajaxIndivRes():
    db.ping(reconnect=True, attempts=1, delay=0)
    data = request.get_json()
    result = getIndiv("bypass", data['id'])
    if result == "Not found":
        session['error'] = True
        return json.dumps({'status': 'OK', 'error': True})
    return json.dumps({'status': 'OK', 'result': result})

@app.route('/edit/reservation/<string:id>/<string:indiv>')
def editreservation(id, indiv):
    db.ping(reconnect=True, attempts=1, delay=0)
    result = getIndiv(id, indiv)
    if result == "Not found":
        session['error'] = True
        return redirect('/')
    else:
        return render_template("edit.html", edit = indiv, type = "reservation")

@app.route('/removelogic', methods=["POST"])
def doRemove():
    db.ping(reconnect=True, attempts=1, delay=0)
    data = request.get_json()
    result = delete(data['id'], data['type'])
    if result == False:
        session['error'] = True
        return json.dumps({'status': 'OK', 'error': True})
    return json.dumps({'status': 'OK'})

@app.route('/editlogic', methods=["POST"])
def doEdit():
    db.ping(reconnect=True, attempts=1, delay=0)
    data = request.get_json()
    new_key = editEntry(data['id'], data['type'], data)
    if new_key == False:
        session['error'] = True
        return json.dumps({'status': 'OK', 'error': True})
    return json.dumps({'status': 'OK', 'result': new_key})

@app.route('/gettaken', methods=["POST"])
def getTaken():
    data = request.get_json()
    if getByID(data['id']) == "Not found":
        session['error'] = True
        return json.dumps({'status': 'OK', 'error': True})
    cursor.execute("SELECT taken FROM DELIVERIES WHERE uuid = %s", (data['id'],))
    return json.dumps({'status': 'OK', 'taken': cursor.fetchone()[0]})

@app.errorhandler(404)
def page_not_found(e):
    session['error'] = True
    return redirect('/')

# FUNCTIONS ------------------------------------------------

addCommand = "INSERT INTO DELIVERIES (start, end, depart, reach, spots, name, phone, email, people, uuid, uni, taken, secret_key, zip_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
def addDeliv(data):
    id = str(uuid.uuid4())
    secret = str(uuid.uuid4())
    deliv = (data['start'], data['dropoff'], data['departure'], data['arrival'], data['spots'], data['name'], data['phone'], data['email'], '', id, data['uni'], 0, secret, data['zip'])
    cursor.execute(addCommand, deliv)
    db.commit()
    ES.addEmail(data['email'], id, secret)
    return id, secret

addVerifyCommand = "INSERT INTO VERIFY (start, end, depart, reach, spots, name, phone, email, people, uuid, uni, taken, secret_key, zip_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
def addVerify(data):
    id = str(uuid.uuid4())
    secret = str(uuid.uuid4())
    deliv = (data['start'], data['dropoff'], data['departure'], data['arrival'], data['spots'], data['name'], data['phone'], data['email'], '', id, data['uni'], 0, secret, data['zip'])
    cursor.execute(addVerifyCommand, deliv)
    db.commit()
    ES.addEmail(data['email'], id, secret)
    return id, secret

def getDeliv(uni):
    command = "SELECT * FROM DELIVERIES WHERE uni = '"+uni+"' AND depart > NOW() AND taken < spots"
    cursor.execute(command)
    result = []
    for x in cursor.fetchall():
        result.append(list(x))
    return result

indivCommand = "INSERT INTO INDIVIDUALS (id_num, name, email, phone, parentid) VALUES (%s, %s, %s, %s, %s)"
def indivDeliv(data):
    id = str(uuid.uuid4())
    row = getByID(data['parentid'])
    if row == "Not found":
        return False
    selectquery = "SELECT * FROM DELIVERIES WHERE uuid = %s"
    cursor.execute(selectquery, (data['parentid'],))
    val = ""
    try:
        val = cursor.fetchall()[0][8] + id + ","
    except:
        return False
    deliv = (id, data['name'], data['email'], data['phone'], data['parentid'])
    cursor.execute(indivCommand, deliv)
    db.commit()
    updatequery = "UPDATE DELIVERIES SET taken = taken + 1 WHERE uuid = %s"
    cursor.execute(updatequery, (data['parentid'],))
    setquery = "UPDATE DELIVERIES SET people = %s WHERE uuid = %s"
    cursor.execute(setquery, (val, data['parentid']))
    db.commit()
    ES.addRegister(data['email'], data['parentid'], id)
    return True

def getByIDProtected(id, secret):
    cursor.execute("SELECT * FROM DELIVERIES WHERE uuid = %s", (id,))
    row = cursor.fetchone()
    if row:
        if row[12] == secret:
            return row
        else:
            return "Not found"
    else:
        return "Not found"

def getByID(id):
    cursor.execute("SELECT * FROM DELIVERIES WHERE uuid = %s", (id,))
    row = cursor.fetchone()
    print(row)
    if row != None:
        print("------- error")
        return [row, id]
    else:
        return "Not found"

def getIndiv(parent, child):
    if parent == "bypass":
        cursor.execute("SELECT * FROM INDIVIDUALS WHERE id_num = %s", (child,))
        row = cursor.fetchone()
        if row:
            return row
        else:
            return "Not found"
    cursor.execute("SELECT * FROM INDIVIDUALS WHERE parentid = %s AND id_num = %s", (parent, child))
    row = cursor.fetchone()
    if row:
        return row
    else:
        return "Not found"

def auto_clear():
    sql = "SELECT uuid FROM DELIVERIES WHERE reach < NOW()"
    cursor.execute(sql)
    results = []
    for row in cursor:
        results.append(row)
    for x in results:
        cursor.execute("DELETE FROM INDIVIDUALS WHERE parentid = %s", (x[0],))
        cursor.execute("DELETE FROM DELIVERIES WHERE uuid = %s", (x[0],))
    db.commit()

def delete(id, request_type):
    if request_type == "reservation":
        cursor.execute("SELECT parentid FROM INDIVIDUALS WHERE id_num = %s", (id,))
        parentid = cursor.fetchone()[0]
        row = getByID(parentid)
        if row != "Not found":
            row = row[0]
        else:
            return False
        cursor.execute("SELECT email FROM INDIVIDUALS WHERE id_num = %s", (id,))
        email = cursor.fetchone()[0]
        sql = "DELETE FROM INDIVIDUALS WHERE id_num = '"+id+"'"
        cursor.execute(sql)
        db.commit()
        sql2 = "UPDATE DELIVERIES SET people = REPLACE(people, '"+id+",', '')"
        cursor.execute(sql2)
        db.commit()
        updatequery = "UPDATE DELIVERIES SET taken = taken - 1 WHERE uuid = %s"
        cursor.execute(updatequery, (parentid,))
        db.commit()
        ES.indivRemove(email, row)
    else:
        row = getByID(id)
        if row != "Not found":
            row = row[0]
        else:
            return False
        cursor.execute("SELECT * FROM INDIVIDUALS WHERE parentid = %s", (id,))
        results = cursor.fetchall()
        for x in results:
            ES.removeEmailIndiv(x[2], row)
        ES.removeEmail(row[7], row)
        sql = "DELETE FROM DELIVERIES WHERE uuid = '"+id+"'"
        cursor.execute(sql)
        db.commit()
        sql2 = "DELETE FROM INDIVIDUALS WHERE parentid = '"+id+"'"
        cursor.execute(sql2)
        db.commit()
    return True

def editEntry(id, request_type, data):
    email_changed = False
    new_key = ""
    if request_type == "reservation":
        if getIndiv("bypass", id) == "Not found":
            return False
        cursor.execute("SELECT email FROM INDIVIDUALS WHERE id_num = %s", (id,))
        row = cursor.fetchone()
        if row[0] != data['email']:
            email_changed = True
        sql = "UPDATE your_table SET name = %s, email = %s, phone = %s WHERE id_num = %s"
        cursor.execute(sql, (data['name'], data['email'], data['phone'], id))
        db.commit()
        if email_changed:
            new_key = str(uuid.uuid4())
            sql = "UPDATE INDIVIDUALS SET id_num = %s WHERE id_num = %s"
            cursor.execute(sql, (new_key, id))
            db.commit()
            sql2 = "UPDATE DELIVERIES SET people = REPLACE(people, '"+id+",', '"+new_key+"')"
            cursor.execute(sql2)
            db.commit()
        cursor.execute("SELECT * FROM INDIVIDUALS WHERE id_num = %s", (new_key,))
        row = cursor.fetchone()
        uni = getByID(row[4])[0][10]
        ES.editReservationEmail(data['email'], row, uni)
    else:
        row = getByID(id)
        if row != "Not found":
            row = row[0]
        else:
            return False;
        cursor.execute("SELECT email FROM DELIVERIES WHERE uuid = %s", (id,))
        row = cursor.fetchone()
        if row[0] != data['email']:
            email_changed = True
            new_key = str(uuid.uuid4())
            sql = "UPDATE DELIVERIES SET secret_key = %s WHERE uuid = %s"
            cursor.execute(sql, (new_key, id))
            db.commit()
        cursor.execute("SELECT * FROM DELIVERIES WHERE uuid = %s", (id,))
        row = cursor.fetchone()
        ES.editEmail(row[7], row)
        cursor.execute("SELECT * FROM INDIVIDUALS WHERE parentid = %s", (id,))
        rows = cursor.fetchall()
        for x in rows:
            ES.editEmailIndiv(x[2], row, x[0])
        sql = "UPDATE DELIVERIES SET start = %s, end = %s, depart = %s, reach = %s, name = %s, phone = %s, email = %s, zip_code = %s WHERE uuid = %s"
        cursor.execute(sql, (data['location'], data['dropoff'], data['departure'], data['arrival'], data['name'], data['phone'], data['email'], data['zip'], id))
        db.commit()
    if email_changed:
        return new_key
    else:
        return "No new key"

def getDelivNarrow(uni, zip_code, filter):
    command = "SELECT * FROM DELIVERIES WHERE uni = '"+uni+"' AND depart > NOW() AND taken < spots"
    cursor.execute(command)
    result = []
    for x in cursor.fetchall():
        distance_km = dist.query_postal_code(str(x[13])[:5], str(zip_code)[:5])
        if (int(distance_km) / 1.609) <= int(filter):
            result.append(list(x))
    return result


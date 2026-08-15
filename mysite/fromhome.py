from flask import Flask, render_template, request, json, session, redirect
from flask_sqlalchemy import SQLAlchemy
import csv
from SQLFunctions import SQLManager
import os
from dotenv import load_dotenv, set_key

load_dotenv()

SQLManager = SQLManager()

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
    SQLManager.ping()
    SQLManager.auto_clear()

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
    SQLManager.ping()
    SQLManager.auto_clear()

    return render_template("about.html", number = deliveries)

@app.route('/addDelivery', methods=["POST"])
def addDelivery():
    global deliveries
    SQLManager.ping()
    data = request.get_json()

    id, secret = SQLManager.addDeliv(data)

    deliveries += 1;
    set_key(dotenv_path=".env", key_to_set="NUM_DELIVERIES", value_to_set=str(deliveries))

    return json.dumps({'status':'OK', 'id': id, 'secret': secret})

@app.route('/getDeliveries', methods=["POST"])
def getDelivery():
    SQLManager.auto_clear()
    data = request.get_json()

    if data['zip_code'] != "":
        results = SQLManager.getDelivNarrow(data['uni'], data['zip_code'], data['filter'])
    else:
        results = SQLManager.getDeliv(data['uni'])
    session['uni'] = data['uni']
    return json.dumps({'status':'OK', 'result': results})

@app.route('/register', methods=["POST"])
def register():
    data = request.get_json()

    result = SQLManager.indivDeliv(data)
    if result == False:
        session['error'] = True
        print("---------- error found")
        return json.dumps({'status': 'OK', 'error': True})
    return json.dumps({'status':'OK'})

@app.route('/edit/delivery/<string:id>/<string:secret>')
def editdelivery(id, secret):
    SQLManager.ping()
    SQLManager.auto_clear()

    result = SQLManager.getByIDProtected(id, secret)
    if result == "Not found":
        session['error'] = True
        return redirect('/')
    else:
        return render_template("edit.html", edit = id, type = "delivery")

@app.route('/view/<string:id>')
def viewdelivery(id):
    SQLManager.ping()
    SQLManager.auto_clear()

    result = SQLManager.getByID(id)
    if result == "Not found":
        session['error'] = True
        return redirect('/')
    else:
        return render_template("index.html", view = str(result[1]))

@app.route('/getDeliveryDetails', methods=["POST"])
def ajaxIndiv():
    SQLManager.ping()
    data = request.get_json()

    result = SQLManager.getByID(data['id'])[0]
    if result == "Not found":
        session['error'] = True
        return json.dumps({'status': 'OK', 'error': True})
    return json.dumps({'status': 'OK', 'result': result})

@app.route('/getDeliveryDetails/res', methods=["POST"])
def ajaxIndivRes():
    SQLManager.ping()
    data = request.get_json()

    result = SQLManager.getIndiv("bypass", data['id'])
    if result == "Not found":
        session['error'] = True
        return json.dumps({'status': 'OK', 'error': True})
    return json.dumps({'status': 'OK', 'result': result})

@app.route('/edit/reservation/<string:id>/<string:indiv>')
def editreservation(id, indiv):
    SQLManager.ping()

    result = SQLManager.getIndiv(id, indiv)
    if result == "Not found":
        session['error'] = True
        return redirect('/')
    else:
        return render_template("edit.html", edit = indiv, type = "reservation")

@app.route('/removelogic', methods=["POST"])
def doRemove():
    SQLManager.ping()
    data = request.get_json()

    result = SQLManager.delete(data['id'], data['type'])
    if result == False:
        session['error'] = True
        return json.dumps({'status': 'OK', 'error': True})
    return json.dumps({'status': 'OK'})

@app.route('/editlogic', methods=["POST"])
def doEdit():
    SQLManager.ping()
    data = request.get_json()

    new_key = SQLManager.editEntry(data['id'], data['type'], data)
    if new_key == False:
        session['error'] = True
        return json.dumps({'status': 'OK', 'error': True})
    return json.dumps({'status': 'OK', 'result': new_key})

@app.route('/gettaken', methods=["POST"])
def getTaken():
    SQLManager.ping()
    data = request.get_json()

    if SQLManager.getByID(data['id']) == "Not found":
        session['error'] = True
        return json.dumps({'status': 'OK', 'error': True})
    #cursor.execute("SELECT taken FROM DELIVERIES WHERE uuid = %s", (data['id'],))
    taken = SQLManager.getTaken(data['id'])
    return json.dumps({'status': 'OK', 'taken': taken[0]})

@app.errorhandler(404)
def page_not_found(e):
    session['error'] = True
    return redirect('/')

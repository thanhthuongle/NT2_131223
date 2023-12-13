from flask import Flask, render_template, jsonify, redirect, request
from random import choice
from datetime import datetime
from flask import Flask
from flask import request, jsonify
from flask_cors import CORS, cross_origin
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.metrics import confusion_matrix
from sklearn.metrics import plot_confusion_matrix
import numpy as np
import cv2
import base64
import json
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import person
import os, binascii
import pandas as pd
import json, database, base64
import seaborn as sns
import csv

def ai_medicine(TTT):
    df = pd.read_csv("datatrainin.csv")
    df.head()
    df['CLASS'].value_counts()
    y = df['CLASS']
    X = df.drop(columns=['CLASS'])
    X_train, X_test, y_train, y_test = train_test_split(X,y, random_state=42, test_size=0.1)
    my_tree = DecisionTreeClassifier(splitter='random')
    my_tree.fit(X_train, y_train)
    TT = [[24,TTT[1],89.0,98.0,1]]
    y_pred = my_tree.predict(TT)
    if y_pred[0] == 0:
      output = ' Paracetamol\n Ibuprofen\n Aspirin\n Naproxen\n'
    if y_pred[0] == 1:
      output= ' Paracetamol\n Verapamil\n Ibuprofen\n Amlodipine\n Felodipine\n Diltiazem\n Atenolol\n Digoxin'
    if y_pred[0] == 2:
      output = ' Vitamin energy\n Ampha 3B\n Becoron C'
    if y_pred[0] == 3:
      output = ' 39, 56, 143Diltiazem\n Atropine\n Adrenalin\n Dopamine\n Amiodarone\n Quinidine'
    return output;

def processCsv(path):
    with open('static/goiythuoc.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        t = []
        for row in csv_reader:
            for i in row:
                t.append(float(i))
        return ai_medicine(t)
        
labelXray = ["Aortic enlargement",
"Atelectasis",
"Calcification",
"Cardiomegaly",
"Consolidation",
"Infiltration",
"Lung Opacity",
"Nodule/Mass",
"Other lesion",
"Pleural effusion",
"Pleural thickening",
"Pneumothorax",
"Pulmonary fibrosis"]

net = cv2.dnn.readNet("yolov4-custom_last.weights", "yolov4-custom.cfg")
scale = 0.00392
conf_threshold = 0.25
nms_threshold = 0.4

def get_output_layers(net):
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    return output_layers

def build_return(class_id, x, y, x_plus_w, y_plus_h):
    return str(class_id) + "," + str(x) + "," + str(y) + "," + str(x_plus_w) + "," + str(y_plus_h)

def detect(image):
    Width = image.shape[1]
    Height = image.shape[0]
    blob = cv2.dnn.blobFromImage(image, scale, (416, 416), (0, 0, 0), swapRB = True, crop=False)
    net.setInput(blob)
    outs = net.forward(get_output_layers(net))
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > conf_threshold:
                center_x = int(detection[0] * Width)
                center_y = int(detection[1] * Height)
                w = int(detection[2] * Width)
                h = int(detection[3] * Height)
                x = center_x - w / 2
                y = center_y - h / 2
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
    retString = ""
    for i in indices:
        box = boxes[i]
        x = box[0]
        y = box[1]
        w = box[2]
        h = box[3]
        retString += build_return(class_ids[i], round(x), round(y), round( w), round( h)) + "|"
        confidences[i] = round(confidences[i],2) 
        encoded_hand = json.dumps((str(confidences[i])))
        decoded_hand = json.loads(encoded_hand)
        thislist = []
        thislist.append(decoded_hand)
    resDecode = retString.split("|")
    resDecode = resDecode[0:len(resDecode) - 1]
    for i in range(len(resDecode)):
        resDecode[i] = resDecode[i].split(",")
    for i in resDecode:
        cv2.rectangle(image, (int(i[1]), int(i[2])), (int(i[1]) + int(i[3]), int(i[2]) + int(i[4])), (255,255,255), 4)
        cv2.putText(image, labelXray[min(int(i[0]), 12)], (int(i[1]), int(i[2]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 3)
    return image;
        
app = Flask(__name__)
logged_in = {}
api_loggers = {}
mydb = database.db(host='localhost',
                                         database='ARMS',
                                         user='root',
                                         password='')

#test api key aGFja2luZ2lzYWNyaW1lYXNmc2FmZnNhZnNhZmZzYQ==

@app.route("/login", methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        user = person.user(request.form['username'], request.form['password'])
        if user.authenticated:
            user.session_id = str(binascii.b2a_hex(os.urandom(15)))
            logged_in[user.username] = {"object": user}
            return redirect('/overview/{}/{}'.format(request.form['username'], user.session_id))
        else:
            error = "invalid Username or Passowrd"
       
    return render_template('Login.htm', error=error)
    
#this links is for device 1 
@app.route('/device1/<string:username>/<string:session>', methods=["GET", "POST"])
def Dashoboard():
    user = {
        "username" : "Aman Singh",
        "image":"static/images/logo1.png"
    }

    devices = [
        {"Dashboard" : "device1",
        "deviceID": "Device1"
        }
    ]
    return render_template('device_dashboard.htm', title='Dashobard', user=user, devices=devices)


#this link is for the main dashboard of the website
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.htm', title='HOME - Landing Page')

@app.route('/overview/<string:username>/<string:session>', methods=['GET', 'POST'])
def overview(username, session):
    global logged_in
    if username in logged_in and (logged_in[username]['object'].session_id == session):
        user = {
            "username" : username,
            "image":"/static/images/logo1.png",
            "api": logged_in[username]["object"].api,
            "session" : session
        }

        devices = [
            {"Dashboard" : "device1",
            "deviceID": "Device1"
            }
        ]
        return render_template('overview.htm', title='Y ta thong minh', user=user, devices=devices)
    
    else:
        return redirect('/login')
        
@app.route('/goiythuoc/<string:username>/<string:session>', methods=['GET', 'POST'])
def goiythuoc(username, session):
    
    global logged_in
    print("Apikey:" + '<string:apikey>')
    if username in logged_in and (logged_in[username]['object'].session_id == session):
        user = {
            "username" : username,
            "image":"/static/images/logo1.png",
            "api": logged_in[username]["object"].api,
            "session" : session
        }

        devices = [
            {"Dashboard" : "device1",
            "deviceID": "Device1"
            }
        ]
        return render_template('goiythuoc.htm', title='Gợi ý thuốc', user=user, devices=devices)
    
    else:
        return redirect('/login')
        
@app.route('/chandoanbenh/<string:username>/<string:session>', methods=['GET', 'POST'])
def chandoanbenh(username, session):
    global logged_in
    print("Apikey:" + '<string:apikey>')
    if username in logged_in and (logged_in[username]['object'].session_id == session):
        user = {
            "username" : username,
            "image":"/static/images/logo1.png",
            "api": logged_in[username]["object"].api,
            "session" : session
        }

        devices = [
            {"Dashboard" : "device1",
            "deviceID": "Device1"
            }
        ]
        return render_template('chandoanbenh.htm', title='Chẩn đoán bệnh', user=user, devices=devices)
    else:
        return redirect('/login')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/kqgoiythuoc/<string:username>/<string:session>', methods=['GET', 'POST'])
def kqgoiythuoc(username, session):
    global logged_in
    print("Apikey:" + '<string:apikey>')
    if username in logged_in and (logged_in[username]['object'].session_id == session):
        user = {
            "username" : username,
            "image":"/static/images/logo1.png",
            "api": logged_in[username]["object"].api,
            "session" : session
        }

        devices = [
            {"Dashboard" : "device1",
            "deviceID": "Device1"
            }
        ]
        file = request.files['file']
        if file:
                file.save("static/goiythuoc.csv")
        kq = processCsv('static/goiythuoc.csv')
        return render_template('kqgoiythuoc.htm', title='Gợi ý thuốc', user=user, devices=devices, kq = kq)
    
    else:
        return redirect('/login')
        
@app.route('/kqchandoanbenh/<string:username>/<string:session>', methods=['GET', 'POST'])
def kqchandoanbenh(username, session):
    
    global logged_in
    print("Apikey:" + '<string:apikey>')
    if username in logged_in and (logged_in[username]['object'].session_id == session):
        user = {
            "username" : username,
            "image":"/static/images/logo1.png",
            "api": logged_in[username]["object"].api,
            "session" : session
        }

        devices = [
            {"Dashboard" : "device1",
            "deviceID": "Device1"
            }
        ]
        file = request.files['file']
        if file:
                file.save("static/xquang.png")


        img = cv2.imread("static/xquang.png")
        img = detect(img)
        cv2.imwrite("static/kqxquang.png", img)
        
        return render_template('kqchandoanbenh.htm', title='Chẩn đoán bệnh', user=user, devices=devices)
    
    else:
        return redirect('/login')
        
@app.route('/apisettings/<string:username>/<string:session>', methods=['GET', 'POST'])
def apisettings(username, session):
    
    global logged_in

    if username in logged_in and (logged_in[username]['object'].session_id == session):
        user = {
            "username" : username,
            "image":"/static/images/logo1.png",
            "api": logged_in[username]["object"].api,
            "session" : session
        }

        devices = [
            {"Dashboard" : "device1",
            "deviceID": "Device1"
            }
        ]
        return render_template('api_settings.htm', title='API-Settings', user=user, devices=devices)
    
    else:
        return redirect('/login')


#this part is for the profile view
@app.route('/profile/<string:username>/<string:session>', methods=['GET', 'POST'])
def profile(username, session):
    
    global logged_in

    if username in logged_in and (logged_in[username]['object'].session_id == session):
        user = {
            "username" : username,
            "image":"/static/images/logo1.png",
            "api": logged_in[username]["object"].api,
            "session" : session,
            "firstname": logged_in[username]["object"].first,
            "lastname": logged_in[username]["object"].last,
            "email":logged_in[username]["object"].email,
            "phone":logged_in[username]["object"].phone,
            "lastlogin":logged_in[username]["object"].last_login,
        }

        devices = [
            {"Dashboard" : "device1",
            "deviceID": "ARMS12012"
            }
        ]
        return render_template('profile.htm', title='API-Settings', user=user, devices=devices)
    
    else:
        return redirect('/login')


@app.route('/logout/<string:username>/<string:session>', methods=['GET', 'POST'])
def logout(username, session):
    
    global logged_in

    if username in logged_in and (logged_in[username]['object'].session_id == session):
        logged_in.pop(username)
        # print("logged out")
        return redirect('/')
    else:
        return redirect('/login')

#this is the testing for api 
@app.route("/api/<string:apikey>/test", methods=["GET", "POST"])
def apitest (apikey):
    return {"data":"working Fine Connected to the api server"}


#get all the devices information from the user
@app.route("/api/<string:apikey>/listdevices", methods=['GET', 'POST'])
def listdevices(apikey):
    global api_loggers
    global mydb
    if not(apikey in api_loggers):
        try:
            query = "select username from users where api_key = '{}'".format(apikey)
            mydb.cursor.execute(query)
            username = mydb.cursor.fetchall()
            username = username[0][0]
            apiuser = person.user(username, "dummy")
            apiuser.authenticated = True
            devices_list = apiuser.get_devices()
            api_loggers[apikey] = {"object" : apiuser}
            return jsonify(devices_list)
        except Exception as e:
            print (e)
            return jsonify({"data":"Oops Looks like api is not correct"})
    
    else:
        data = api_loggers[apikey]["object"].get_devices()
        return jsonify (data)

randlist = [i for i in range(0, 100)]

@app.route('/api/<string:apikey>/deviceinfo/<string:deviceID>', methods=['GET', 'POST'])
def device_info (apikey, deviceID):
    global api_loggers
    global mydb
    if not(apikey in api_loggers):
        try:
            query = "select username from users where api_key = '{}'".format(apikey)
            mydb.cursor.execute(query)
            username = mydb.cursor.fetchall()
            username = username[0][0]
            apiuser = person.user(username, "dummy")
            apiuser.authenticated = True
            data = apiuser.dev_info(deviceID)
            api_loggers[apikey] = {"object" : apiuser}
            #this part is hard coded so remove after fixing the issue
            data = list(data)
            data[2] = "Rosegarden"
            ret = ""
            for i in data: 
                ret = ret + " " + str(i)
            ret = ret[1:]
            return ret
        except Exception as e:
            print (e)
            return jsonify({"data":"Oops Looks like api is not correct"})
    
    else:
        data = api_loggers[apikey]["object"].dev_info(deviceID)

        #this part is hard coded so remove after fixing the issue
        data = list(data)
        data[2] = "Rosegarden"
        ret = ""
        for i in data: 
            ret = ret + " " + str(i)
        ret = ret[1:]
        return ret

@app.route('/api/<string:apikey>/fieldstat/<string:fieldname>', methods=['GET', 'POST'])
def fieldstat (apikey, fieldname):
    
    global api_loggers
    global mydb
    if not(apikey in api_loggers):
        try:
            query = "select username from users where api_key = '{}'".format(apikey)
            mydb.cursor.execute(query)
            username = mydb.cursor.fetchall()
            username = username[0][0]
            apiuser = person.user(username, "dummy")
            apiuser.authenticated = True
            data = apiuser.field_values(fieldname)
            api_loggers[apikey] = {"object" : apiuser}
            return jsonify(data)
        except Exception as e:
            print (e)
            return jsonify({"data":"Oops Looks like api is not correct"})
    
    else:
        data = api_loggers[apikey]["object"].field_values(fieldname)
        return jsonify (data)


@app.route('/api/<string:apikey>/devicestat/<string:fieldname>/<string:deviceID>', methods=['GET', 'POST'])
def devicestat (apikey, fieldname, deviceID):
    
    global api_loggers
    global mydb
    if not(apikey in api_loggers):
        try:
            query = "select username from users where api_key = '{}'".format(apikey)
            mydb.cursor.execute(query)
            username = mydb.cursor.fetchall()
            username = username[0][0]
            apiuser = person.user(username, "dummy")
            apiuser.authenticated = True
            data = apiuser.device_values(fieldname, deviceID)
            api_loggers[apikey] = {"object" : apiuser}
            return jsonify(data)
        except Exception as e:
            print (e)
            return jsonify({"data":"Oops Looks like api is not correct"})
    
    else:
        data = api_loggers[apikey]["object"].device_values(fieldname, deviceID)
        return jsonify (data)

@app.route('/api/<string:apikey>/update/<string:data>', methods=['GET','POST'])
def update_values(apikey, data):
    global mydb
    try:
        data = decode(data)
        output = mydb.get_apikeys()
        if True:#apikey in output:
            if (len(data) == 6) and (type(data) is list):
                fieldname = data[0]
                deviceID = data[1]
                temp = data[2]
                humidity = data[3]
                moisture = data[4]
                light = data[5]
                mydb.update_values(apikey, fieldname, deviceID, temp, humidity, moisture, light)
                return ("Values Updated")
            else:
                return "Data Decoding Error!"
        else:
            return "Api key invalid"

    except Exception as e:
        print (e)
        return jsonify({"data":"Oops Looks like api is not correct"})
        
@app.route('/api123/<string:data>', methods=['GET','POST'])
def update_values123():
    print("123123")
    return("123123")

@app.route("/api/<string:apikey>/temperature", methods=["GET", "POST"])
def get_temperature(apikey):
    
    randData = choice(randlist)
    time = datetime.now()
    time = time.strftime("%H:%M:%S")
    response = [time, randData]
    return jsonify(response)

@app.route("/api/<string:apikey>/moisture", methods=["GET", "POST"])
def get_moisture(apikey):
    
    randData = choice(randlist)
    time = datetime.now()
    time = time.strftime("%H:%M:%S")
    response = [time, randData]
    return jsonify(response)

@app.route("/api/<string:apikey>/humidity", methods=["GET", "POST"])
def get_humidity(apikey):
    
    randData = choice(randlist)
    time = datetime.now()
    time = time.strftime("%H:%M:%S")
    response = [time, randData]
    return jsonify(response)

@app.route("/api/<string:apikey>/light", methods=["GET", "POST"])
def get_light(apikey):
    randData = choice(randlist)
    time = datetime.now()
    time = time.strftime("%H:%M:%S")
    response = [time, randData]
    return jsonify(response)

def encode(data):
    data = json.dumps(data)
    message_bytes = data.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message

def decode(base64_message):
    base64_bytes = base64_message.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('ascii')
    return json.loads(message)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 1235, debug=True)
    

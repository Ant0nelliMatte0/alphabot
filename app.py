
from crypt import methods
from errno import ESTALE
import imp
from flask import Flask, jsonify, render_template, request,redirect,url_for,make_response
import RPi.GPIO as GPIO
import time
import socket as sck
import sqlite3
import random
import string
from datetime import datetime
app = Flask(__name__)
date= ""
token= ""

DL = 19
DR = 16
for _ in range(0,20):
    c = random.choice(string.ascii_letters)
    token = token + c


def validate(username, password):
    completion = False
    con = sqlite3.connect('./alfabot.db')
    #with sqlite3.connect('static/db.db') as con:
    cur = con.cursor()
    cur.execute("SELECT * FROM Users")
    rows = cur.fetchall()
    for row in rows:
        dbUser = row[0]
        dbPass = row[1]
        if dbUser==username:
            completion=check_password(dbPass, password)
    con.close()
    return completion

def check_password(hashed_password, user_password):
    return hashed_password == user_password

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username)
        print(password)
        completion = validate(username, password)
        if completion ==False:
            error = 'Invalid Credentials. Please try again.'
        else:
            cookie = request.cookies.get('username')
            if cookie == None:
                resp = make_response(redirect(url_for('index')))
                resp.set_cookie('username',username)
            else:
                resp = make_response(redirect(url_for('index')))
            date = datetime.today()
            con = sqlite3.connect('./alfabot.db')
            cur = con.cursor()
            cur.execute(f"INSERT INTO accessi (user,date) VALUES ('{username}','{date}')  ")
            con.close()
            return resp
    return render_template('login.html', error=error)


@app.route(f'/{token}', methods=['GET', 'POST'])
def index():
    user = request.cookies.get('username')
    if request.method == 'POST':
        if request.form.get('action_forward') == 'forward':
            print("go forward")
            movimento = "forward"
            Ab.forward(3)
        elif  request.form.get('action_backward') == 'backward':
            print("go backward")
            movimento = "backward"
            Ab.backward(3)
        elif  request.form.get('action_turn_right') == 'turn_right':
            print("turn right")
            movimento = "turn_right"
            Ab.right(0.75)
        elif  request.form.get('action_turn_left') == 'turn_left':
            print("turn left")
            movimento = "turn_left"
            Ab.left(0.75)
        elif request.form.get('action_stop') == 'stop':
            movimento = "stop"
            print("stop")
            Ab.stop()
        elif request.form.get('do_movement') == 'movement':
            movimento = request.form['movimento']
            con = sqlite3.connect('alfabot.db')
            cur = con.cursor()
            cur.execute(f"SELECT sequenza FROM movimenti WHERE movimento = '{movimento}'")  #query che mi permette di selezionare la sequenza con il nome del messaggio ricevuto
            rows = cur.fetchall()   #salvo il risultato
            con.close()
            if len(rows) == 0:
                print("ERRORE")
            tmp = rows[0]
            seq = tmp[0]   #mi salvo la sequenza(che fa parte di una tupla)
            print(seq)
            coms = seq.split(",")  #divido i singoli comandi
            print(coms)
            con.close()
            for com in coms:            #ciclo su tutti i singoli comandi
                par = com.split(":")   #separo la direzione dal tempo di esecuzione 
                if par[0] == "w":       #confronto la direzione ricevuta con tutte quelle disponibili
                    print("avanti")
                    Ab.forward(float(par[1]))  #passo al metodo anche il tempo per cui dev'essere eseguito il movimento
                if par[0] == "a":
                    print("sinistra")
                    Ab.left(float(par[1]))
                if par[0] == "s":
                    print("indietro")
                    Ab.backward(float(par[1]))
                if par[0] == "d":
                    print("destra")
                    Ab.right(float(par[1]))
                if par[0] == "b":
                    print("stop")
                    Ab.stop(float(par[1]))     
        else:
            print("Unknown")
        con = sqlite3.connect('alfabot.db')
        cur = con.cursor()
        cur.execute(f"SELECT NA FROM accessi WHERE(user ='{user}' AND  date ='{date}')")
        NA = cur.fetchall()
        cur.execute(f"INSERT INTO comandi (NA,utente,movimento) VALUES ('{NA[0]}','{user}','{movimento}')")
        con.close()
    elif request.method == 'GET':
        return render_template('index.html')
    return render_template("index.html")

@app.route('/api/v1/sensors/obstacles',methods = ['GET','POST'])
def api_obstacles():
    DL_status = GPIO.input(DL)
    DR_status = GPIO.input(DR)
    dizionario = {'right':DR_status,'left':DL_status}
    return jsonify(dizionario)

@app.route('/api/v1/motors/left',methods = ['GET','POST'])
def api_motor_left():
    try:
        if 'pwm' in request.args:
            pwm = float(request.args['pwm'])
        if 'time' in request.args:
            t = float(request.args['time'])
        Ab.set_motor(pwm,0)
        time.sleep(t)
        Ab.stop()
        return '1'
    except:
        return '0'
    
@app.route('/api/v1/motors/right',methods = ['GET','POST'])
def api_motor_right():
    try:
        if 'pwm' in request.args:
            pwm = float(request.args['pwm'])
        if 'time' in request.args:
            t = float(request.args['time'])
        Ab.set_motor(0,pwm)
        time.sleep(t)
        Ab.stop()
        return '1'
    except:
        return '0'
    
@app.route('/api/v1/motors/both',methods = ['GET','POST'])
def api_motor_both():
    try:
        if 'pwm' in request.args:
            pwm = float(request.args['pwm'])
        if 'time' in request.args:
            t = float(request.args['time'])
        Ab.set_motor(pwm,pwm)
        time.sleep(t)
        Ab.stop()
        return '1'
    except:
        return '0'

    
class AlphaBot():  
    
    def __init__(self, in1=13, in2=12, ena=6, in3=21, in4=20, enb=26):
        self.IN1 = in1
        self.IN2 = in2
        self.IN3 = in3
        self.IN4 = in4
        self.ENA = ena
        self.ENB = enb
        self.PA  = 50
        self.PB  = 50

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.IN1, GPIO.OUT)
        GPIO.setup(self.IN2, GPIO.OUT)
        GPIO.setup(self.IN3, GPIO.OUT)
        GPIO.setup(self.IN4, GPIO.OUT)
        GPIO.setup(self.ENA, GPIO.OUT)
        GPIO.setup(self.ENB, GPIO.OUT)
        self.PWMA = GPIO.PWM(self.ENA,500)
        self.PWMB = GPIO.PWM(self.ENB,500)
        self.PWMA.start(self.PA)
        self.PWMB.start(self.PB)
        self.stop()

    def left(self,t, speed):
        self.PWMA.ChangeDutyCycle(speed)
        self.PWMB.ChangeDutyCycle(speed)
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.HIGH)
        GPIO.output(self.IN4, GPIO.LOW)
        time.sleep(t)
        self.stop()

    def stop(self):
        self.PWMA.ChangeDutyCycle(0)
        self.PWMB.ChangeDutyCycle(0)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.LOW)
        

    def right(self,t, speed=30):
        self.PWMA.ChangeDutyCycle(speed)
        self.PWMB.ChangeDutyCycle(speed)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.HIGH)
        time.sleep(t)    #faccio eseguire il movimento per un determinato tempo 't'
        self.stop()     #fermo il movimento

    def forward(self,t,speed=30):
        self.PWMA.ChangeDutyCycle(speed)
        self.PWMB.ChangeDutyCycle(speed)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        GPIO.output(self.IN3, GPIO.HIGH)
        GPIO.output(self.IN4, GPIO.LOW)
        time.sleep(t)
        self.stop()


    def backward(self,t, speed=30):
        self.PWMA.ChangeDutyCycle(speed)
        self.PWMB.ChangeDutyCycle(speed)
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.HIGH)
        time.sleep(t)
        self.stop()
        
    def set_pwm_a(self, value):
        self.PA = value
        self.PWMA.ChangeDutyCycle(self.PA)

    def set_pwm_b(self, value):
        self.PB = value
        self.PWMB.ChangeDutyCycle(self.PB)    
        
    def set_motor(self, left, right):
        right=-right
        if (right >= 0) and (right <= 100):
            GPIO.output(self.IN1, GPIO.HIGH)
            GPIO.output(self.IN2, GPIO.LOW)
            self.PWMA.ChangeDutyCycle(right)
        elif (right < 0) and (right >= -100):
            GPIO.output(self.IN1, GPIO.LOW)
            GPIO.output(self.IN2, GPIO.HIGH)
            self.PWMA.ChangeDutyCycle(0 - right)
        if (left >= 0) and (left <= 100):
            GPIO.output(self.IN3, GPIO.HIGH)
            GPIO.output(self.IN4, GPIO.LOW)
            self.PWMB.ChangeDutyCycle(left)
        elif (left < 0) and (left >= -100):
            GPIO.output(self.IN3, GPIO.LOW)
            GPIO.output(self.IN4, GPIO.HIGH)
            self.PWMB.ChangeDutyCycle(0 - left)


if __name__ == '__main__':
    Ab = AlphaBot()
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(DR,GPIO.IN,GPIO.PUD_UP)
    GPIO.setup(DL,GPIO.IN,GPIO.PUD_UP)
    app.run(debug=True, host='0.0.0.0')
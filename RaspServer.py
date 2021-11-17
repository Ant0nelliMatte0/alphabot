import time
import RPi.GPIO as GPIO
import socket as sck
import sqlite3

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

    def left(self,t, speed=30):
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
def run():
    s = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
    s.bind(('0.0.0.0', 5000))
    s.listen()  #mi metto in ascolto
    print("listening")
    conn, addr = s.accept()  #mi connetto con il client
    print("connected")
    try:
        while True:
            data = conn.recv(4096)  #ricevo dal client
            msg = data.decode().upper()  #salvo il messaggio
            print("received")
            print(msg)
            con = sqlite3.connect('alfabot.db')
            cur = con.cursor()
            query = f"SELECT sequenza FROM movimenti WHERE movimento = '{msg}'" #query che mi permette di selezionare la sequenza con il nome del messaggio ricevuto
            print(query)
            cur.execute(query) #eseguo la query
            rows = cur.fetchall()   #salvo il risultato
            if len(rows) == 0:
                print("ERRORE")
            tmp = rows[0]
            seq = tmp[0]   #mi salvo la sequenza(che fa parte di una tupla)
            print(seq)
            coms = seq.split(",")  #divido i singoli comandi
            print(coms)
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
    except KeyboardInterrupt:
        GPIO.cleanup()

if __name__ == '__main__':

    Ab = AlphaBot()
    run()

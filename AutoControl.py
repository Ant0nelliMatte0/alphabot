import requests
import json

ip = input("inserisci l'ip: ")

while True:
    r = requests.get(f"http://{ip}:5000/api/v1/sensors/obstacles")
    data = r.json()
    if data['left'] == 1 and data['right'] == 1:
        requests.get(f"http://{ip}:5000/api/v1/motors/both?pwm=40&time=0.65")
    else:
        r = requests.get(f"http://{ip}:5000/api/v1/motors/left?pwm=35&time=0.65")
        r = requests.get(f"http://{ip}:5000/api/v1/motors/both?pwm=-35&time=0.28")
        r = requests.get(f"http://{ip}:5000/api/v1/motors/left?pwm=35&time=0.45")
        r = requests.get(f"http://{ip}:5000/api/v1/motors/both?pwm=-35&time=0.28")
        r = requests.get(f"http://{ip}:5000/api/v1/sensors/obstacles")
        data = r.json()
        if data['right'] == 0 or data['left'] == 0:
            r = requests.get(f"http://{ip}:5000/api/v1/motors/right?pwm=35&time=0.90")
            r = requests.get(f"http://{ip}:5000/api/v1/motors/both?pwm=-35&time=0.28")
            r = requests.get(f"http://{ip}:5000/api/v1/motors/right?pwm=35&time=0.90")
            r = requests.get(f"http://{ip}:5000/api/v1/motors/both?pwm=-35&time=0.28")
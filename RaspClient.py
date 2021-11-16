import socket as sck

s = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
s.connect(('192.168.0.142',6000)) #mi connetto al raspberry

while True:
    d = input("inserisci il movimento: ").upper() #inserisco il nome del movimento da eseguire
    s.sendall(d.encode())    #lo madno
s.close()


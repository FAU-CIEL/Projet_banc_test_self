import serial
import time
import re

PORT = "COM20"
BAUDRATE = 115200

esp32 = None

def envoyer_trame(trame):
    global esp32
    try:
        if esp32 == None:
            esp32 = serial.Serial(PORT, BAUDRATE, timeout=5)
        time.sleep(1)
        esp32.write(trame.encode() + b"\n")
    except serial.SerialException as e:
        print(f"Erreur série : {e}")

def recevoir_trame():
    global esp32
    if esp32 is not None:
        try:
            trame_recue = ""
            while not re.search("OK;CMD;",trame_recue):
                trame_recue = esp32.readline().decode().strip()
                if re.search("ERR;", trame_recue):
                    print("Erreur reçue : " + trame_recue)
                    break
                print(trame_recue)

        except serial.SerialException as e:
            print(f"Erreur série : {e}")

if __name__ == "__main__":
    trame = ["SET_CONF", "START", "GET_STATUS", "RESET", "recevoir", "test"]
    envoyer_trame(trame[0] + ";nb=15;f=20")
    recevoir_trame()
    envoyer_trame(trame[1])
    recevoir_trame()
    #envoyer_trame(trame[-1]) #test trame non reconnue
    #recevoir_trame()
    #envoyer_trame(trame[2])
    #recevoir_trame()
    #envoyer_trame(trame[4])
    #recevoir_trame()
    #envoyer_trame("test45")
    #recevoir_trame()


    # erreur paramètre -> envoie quand meme json ?????
    # probleme get_status 
    # garder parametre de sim apres reset (utilser un fichier temp ?)
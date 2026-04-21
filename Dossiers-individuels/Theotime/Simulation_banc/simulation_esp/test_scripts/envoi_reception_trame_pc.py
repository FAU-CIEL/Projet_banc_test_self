import serial
import time

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
            while True:
                trame_recue = esp32.readline().decode().strip()
                print(trame_recue)
            #return trame_recue
        except serial.SerialException as e:
            print(f"Erreur série : {e}")

if __name__ == "__main__":
    trame = ["SET_CONF", "START", "STOP", "GET_MEAS", "GET_STATUS", "RESET", "MEAS", "recevoir"]
    envoyer_trame(trame[6])# + ";nb=50;f=8")
    print(recevoir_trame())
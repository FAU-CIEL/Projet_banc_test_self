import serial
import json
import time
import re

PORT = "COM20"
BAUDRATE = 115200
OUTPUT_FILE = "D:/fauret.SNIRW/Projet_banc_test_self/Dossiers-individuels/Theotime/Simulation_banc/simulation_esp/LOG/data_recu.json"

data = {}

def receive_json():
    try:
        valeur_json = ""
        esp32 = serial.Serial(PORT, BAUDRATE, timeout=5)
        time.sleep(1)
        esp32.write(b"recevoir\n")
        while True:
                valeur_json = esp32.readline().decode().strip()
                print(valeur_json)
                if valeur_json:
                    if re.search(re.escape('{'), str(valeur_json)):
                        print(valeur_json, flush=True)
                        
                        with open(OUTPUT_FILE, 'w') as file:
                            dict_json =  json.loads(valeur_json)
                            json.dump(dict_json, file)
                        file.close()
                        
                        break

    except serial.SerialException as e:
        print(f"Erreur série : {e}")


def charger_dict():
    with open(OUTPUT_FILE, 'r') as f:
        data_json = json.load(f)
    f.close()
    return data_json


if __name__ == "__main__":
    receive_json()
    """data = charger_dict()
    print(data)
    print("temps : ", data["temps"])
    print("intnensiter : ", data["intensite"])
    print("tension : ", data["tension"])"""

# convertir byte en type pour json
# erreur decode
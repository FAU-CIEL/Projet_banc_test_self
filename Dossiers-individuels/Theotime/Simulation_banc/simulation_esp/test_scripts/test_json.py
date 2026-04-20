import os
import errno
import sys
import io
import json

chemin_PC = "D:/fauret.SNIRW/Projet_banc_test_self/Dossiers-individuels/Theotime/Simulation_banc/simulation_esp/LOG/log.json"
chemin_ESP = os.getcwd() + "LOG/log_esp.json"

data = {
    "name": "theotime",
    "age": 20,
    "city": "Lyon"
}

def test_json():
    if sys.platform == "esp32":
        try:
            file = io.open(chemin_ESP, "w")
        except OSError as e:
            if e.errno == errno.ENOENT:
                os.mkdir(os.getcwd() + "/LOG/")
                file = test_json()
    else:
        file = io.open(chemin_PC, "w")
    return file


file = test_json()

json.dump(data, file)
file.close()

#print(os.listdir())
#print(os.listdir("D:/fauret.SNIRW/Projet_banc_test_self/Dossiers-individuels/Theotime/Simulation_banc/simulation_esp"))
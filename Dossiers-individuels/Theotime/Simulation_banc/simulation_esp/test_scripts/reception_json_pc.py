import serial

PORT = "COM20"
BAUDRATE = 115200
OUTPUT_FILE = "D:/fauret.SNIRW/Projet_banc_test_self/Dossiers-individuels/Theotime/Simulation_banc/simulation_esp/LOG/data_recu.json"

def save_file(data):
    with open(OUTPUT_FILE,'a') as f:
        f.write(data)

def receive_json():
    try:
        esp32 = serial.Serial(PORT, BAUDRATE, timeout=5)
        esp32.write(b"recevoir\n")
        text = str(esp32.read_until(b"}"))
        text = text[2:]
        text = text[:-1]
        text_parse = text.split("\\r\\n")
        print(text_parse)
        for line in range(len(text_parse)):
            save_file(text_parse[line])
        print("fichier reçu avec succès: ", OUTPUT_FILE)

    except serial.SerialException as e:
        print(f"Erreur série : {e}")

if __name__ == "__main__":
    receive_json()
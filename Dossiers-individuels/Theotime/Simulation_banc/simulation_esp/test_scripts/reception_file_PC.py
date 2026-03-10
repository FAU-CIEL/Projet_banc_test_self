import serial

PORT = "COM20"
BAUDRATE = 115200
OUTPUT_FILE = "D:/fauret.SNIRW/Projet_banc_test_self/Dossiers-individuels/Theotime/Simulation_banc/simulation_esp/LOG/data_recu.json"

def receive_file():
    try:
        esp32 = serial.Serial(PORT, BAUDRATE, timeout=5)
        
        with open(OUTPUT_FILE, 'w') as f:
            while True:
                line = esp32.readline().decode(errors='ignore').strip()
                if line == "__END__":
                    print("Fichier reçu avec succès : ", OUTPUT_FILE)
                    break
                if line == "__START__\n":
                    continue
                f.write(str(line) + "\n")
    except serial.SerialException as e:
        print(f"Erreur série : {e}")

if __name__ == "__main__":
    receive_file()
import serial

PORT = "COM20"
BAUDRATE = 115200
OUTPUT_FILE = "D:/fauret.SNIRW/Projet_banc_test_self/Dossiers-individuels/Theotime/Simulation_banc/simulation_esp/LOG/data_recu.json"

def receive_file():
    try:
        esp32 = serial.Serial(PORT, BAUDRATE, timeout=5)
        text = esp32.read_until(b"__END__").decode(errors='ignore') # lit jusqu'au marqueur de fin
        
        text = text.split("__START__")[-1] # suprime tout ce qui précède le marqueur de début
        text = text.replace("__END__", "") # suprime le marqueur de fin
        text = text.strip() # suprime les whitespace superflus
        
        with open(OUTPUT_FILE, 'w') as f:
            f.write(text)
        print("Fichier reçu avec succès : ", OUTPUT_FILE)

    except serial.SerialException as e:
        print(f"Erreur série : {e}")

if __name__ == "__main__":
    receive_file()
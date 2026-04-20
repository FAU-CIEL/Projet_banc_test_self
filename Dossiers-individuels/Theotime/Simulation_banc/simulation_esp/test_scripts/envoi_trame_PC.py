import serial

PORT = "COM20"
BAUDRATE = 115200

def envoi_trame(trame):
    try:
        esp32 = serial.Serial(PORT, BAUDRATE, timeout=5)
        esp32.write(trame)

        esp32.close()
        print("Trame envoyée avec succès.")
    except serial.SerialException as e:
        print(f"Erreur série : {e}")

if __name__ == "__main__":
    trame = b"test_envoi_trame"
    envoi_trame(trame)
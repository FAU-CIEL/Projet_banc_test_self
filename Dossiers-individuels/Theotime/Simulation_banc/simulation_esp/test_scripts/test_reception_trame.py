import machine # type: ignore
import select

BAUDRATE = 115200
OUTPUT_FILE = "trame_recue.txt"


def reception_trame():
    poller = select.poll()
    conexion_IHM = machine.UART(0, BAUDRATE)
    poller.register(conexion_IHM, select.POLLIN)
    trame = ""
    while True:
        #if conexion_IHM.any():
        events = poller.poll(1000)
        if not events:
            continue
        for obj, event in events:
            if event & select.POLLIN & conexion_IHM.any():
                trame = obj.readline()
                #trame = conexion_IHM.read().decode('utf-8') if trame != "" else ""
        
        with open(OUTPUT_FILE, 'w') as f:
            f.write(trame)
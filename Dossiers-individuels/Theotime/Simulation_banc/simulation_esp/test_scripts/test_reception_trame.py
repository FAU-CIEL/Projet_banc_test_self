import machine # type: ignore
import select
import sys
import time

BAUDRATE = 115200
OUTPUT_FILE = "trame_recue.txt"
led = machine.Pin(2, machine.Pin.OUT)

def reception_trame():
    while True:
        led.value(not led.value())
        time.sleep(0.5)
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            trame = sys.stdin.readline().strip()

            with open(OUTPUT_FILE, 'a') as f:
                f.write(trame)
import machine # type: ignore
import sys


led = machine.Pin(2, machine.Pin.OUT)
while True:
    led.on()
    ligne = ""
    with open("text.txt", "a") as f:
        while not ligne:
            ligne = sys.stdin.readline()
            led.off()
            if ligne:
                f.write(ligne)
                f.flush()
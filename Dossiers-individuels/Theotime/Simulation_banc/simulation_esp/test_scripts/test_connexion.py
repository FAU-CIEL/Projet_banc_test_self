import machine
import select
import sys

led = machine.Pin(2, machine.Pin.OUT)
while True:
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        led.value(not led.value())
        with open("text.txt", "a") as f:
            f.write(sys.stdin.readline())
        break
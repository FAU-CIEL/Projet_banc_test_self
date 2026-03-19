import machine # type: ignore
import time

led = machine.Pin(2, machine.Pin.OUT)

def blink():
    while True:
        led.value(not led.value())
        time.sleep(0.5)
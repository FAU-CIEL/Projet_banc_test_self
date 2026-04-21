import Classes # type: ignore
import machine # type: ignore
import time 

while True:
    banc_de_self = Classes.Gestion_fonction()
    banc_de_self.loop()

    time.sleep(10) # evite le pipelining

    # permet de suprimer les données les objets python et variables de la memoire. permet d'eviter "memory allocation fail"
    machine.soft_reset()
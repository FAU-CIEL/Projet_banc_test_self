import Classes # type: ignore
import machine # type: ignore
import errno


led_erreur = machine.Pin(2, machine.Pin.OUT)
led_erreur.on()
banc_de_self = Classes.Gestion_fonction()
banc_de_self.Simulation_banc.t = [1.0,2.0,3.0]
banc_de_self.Simulation_banc.i_l = [2.0,4.0,6.0,8.0]
banc_de_self.Simulation_banc.u_l = [5.0,10.0,15.0,20.0,25.0]
banc_de_self.loop()
led_erreur.off()

"""
while True:
    try:
        banc_de_self.loop()
    except errno as e:
        led_erreur.on()
        break
        """
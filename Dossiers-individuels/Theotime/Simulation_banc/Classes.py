import machine                      # Classe pour la led        # type: ignore 
import select                       # classe detection evenements
import errno                        # classe erreurs
import json                         # classe .Json
import math                         # classe operations mathematiques
import time                         # classe pour le temps
import sys                          # classe systeme (environement + entrée/sortie)
import io                           # classe flux entree/sortie
import os                           # classe systeme (gestion fichiers)


led_pret = machine.Pin(2, machine.Pin.OUT)

# classe pour la reception des trames de commande/parametrage
class Gestion_Reception:
    def __init__(self) -> None:
        self.__trame = ""
        self.trame_correct = False
        self.__liste_code_err = [1, 2, 3, 4, 5, 6, 7, 8, 9] # a revoir
        self.__liste_commande = ["SET_CONF", "START", "STOP", "GET_MEAS", "GET_STATUS", "RESET", "MEAS", "ERR;", "recevoir\n"]
        self.action = ""
        self.parametre_sim = [0, 0]        
        """
        Premier arg => nb echantillon
        Deuxieme arg => frequence d'echantillonage
        """

    def reception_trame(self) -> None:
        self.__trame = ""
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            self.__trame = sys.stdin.readline()
            with open("text.txt", 'a') as f:
                f.write(self.__trame)
            f.close()

    def __chaine_presente(self, commande) -> bool:
        return True if commande in self.__trame else False

    def decoupage_trame(self) -> None:
        if self.__chaine_presente(self.__liste_commande[0]): # SET_CONF
            trame_split = self.__trame.split(";")
            self.parametre_sim[0] = int(trame_split[1].split('=')[1])
            self.parametre_sim[1] = int(trame_split[2].split('=')[1])

    def action_trame(self) -> None:
        for i in range(len(self.__liste_commande)):
            if self.__chaine_presente(self.__liste_commande[i]):
                self.trame_correct = True
                self.action = self.__liste_commande[i]
                self.decoupage_trame()
                break
            else:
                self.trame_correct = False


# classe qui simule le circuit (equa diff + transformer en Z)
class Simulation:
    def __init__(self) -> None:
        # parametre physique
        self.__L = 0
        self.__C = 0

        # condition initial
        self.__U0 = 0

        # gestion du temps
        self.__dt = 0       # pas de temps
        self.__n_steps = 0  # nb d'etapes

        self.__omega0 = 0
        self.__phi = 0

        # tableaux de sorties
        self.t = []
        self.u_l = []
        self.i_l = []

    def init_parametre(self, L, C, U0, dt, nb_step) -> None:
        self.__L = L
        self.__C = C
        self.__U0 = U0
        self.__dt = dt
        self.__n_steps = nb_step
        self.__omega0 = 1 / math.sqrt(self.__L * self.__C)
        self.__phi = 0

        self.t = []
        self.u_l = []
        self.i_l = []

    def __calcul_tension(self, t) -> float:
        return self.__U0 * math.cos(self.__omega0 * t + self.__phi)
    
    def __calcul_intensite(self, t) -> float:
        return self.__C * self.__U0 * math.sin(self.__omega0 * t)

    def __transformer_Z_tension(self, z) -> float:
        return self.__U0 * ((z**2 - z * math.cos(self.__omega0)) / (z**2 - 2 * z * math.cos(self.__omega0) + 1))
    
    def __transformer_Z_intensite(self, z) -> float:
        return self.__C * self.__U0 * self.__omega0 * ((z * math.sin(self.__omega0)) / (z ** 2 -2 * z * math.cos(self.__omega0) + 1))
    
    def simulation(self) -> None:
        for N in range(self.__n_steps):
            self.t.append(self.__dt * N)
            self.u_l.append(self.__transformer_Z_tension(self.t[N]))
            self.i_l.append(self.__transformer_Z_intensite(self.t[N]))

# classe qui stocke les valeurs dans un json
class Gestion_json:
    def __init__(self) -> None:
        self.__chemin_json = "LOG"
        self.__fichier_json = "donnees_self.json"
        self.__donner_a_stocker = {
            "temps": [],
            "tension": [],
            "intensite": []
            }

    def __dossier_existant(self) -> bool:
        for dossier in os.ilistdir():
            nom_dossier, type_, *_ = dossier
            if type_ == 0x4000 and nom_dossier == self.__chemin_json:  # type 0x4000 = dossier
                return True
        return False
    
    def __fichier_existant(self) -> bool:
        for file in os.ilistdir(self.__chemin_json):
            nom_file, type_, *_ = file
            if type_ == 0x8000 and nom_file == self.__fichier_json:     # type 0x8000 = fichier
                return True
        return False
    
    def __creer_chemin_json(self) -> None:
        if not self.__dossier_existant():
            os.mkdir(self.__chemin_json)
    
    def creer_json(self) -> None:
        if sys.platform == "esp32":
            self.__creer_chemin_json()
            os.chdir(self.__chemin_json)
            io.open(self.__fichier_json, 'w')

    def preparation_donnee(self, donnee, valeur) -> None:
        self.__donner_a_stocker[donnee] = valeur
    
    def charger_json(self) -> None:
        with io.open(self.__fichier_json, 't') as file:
            json.dump(self.__donner_a_stocker, file)
        file.close()

    def __detruire_file(self) -> None:
        os.chdir("/" + self.__chemin_json)
        os.remove(self.__fichier_json)

    def detruire_json(self) -> None:
        if sys.platform == "esp32":
            os.chdir("/")
            if self.__dossier_existant():
                if self.__fichier_existant():
                    self.__detruire_file()
                os.chdir("/")
                os.rmdir(self.__chemin_json)

# classe qui renvoie les données a l'IHM
class Gestion_envoi:
    def __init__(self) -> None:
        self.__chemin_fichier_json = "LOG"
        self.__fichier_json = "donnees_self.json"

    def __fichier_existant(self) -> bool:
        if sys.platform == "esp32":
            os.chdir("/" + self.__chemin_fichier_json)
            for fichier in os.ilistdir():
                nom_fichier, type_, *_ = fichier
                if type_ == 0x8000 and nom_fichier == self.__fichier_json: # type 0x8000 = fichier
                    return True
        return False

    def __sortie_prete(self) -> bool:
        poller = select.poll()
        poller.register(sys.stdout, select.POLLOUT)
        events = poller.poll()
        for obj, event in events:
            if event == select.POLLOUT:
                return True
            else:
                return False

    def envoi_donnees(self) -> None:
        if self.__sortie_prete() and self.__fichier_existant():
            with io.open(self.__fichier_json, 'r') as file:
                for line in file:
                    sys.stdout.write(line.strip())

# classe qui gere les autres fonctions
class Gestion_fonction:
    def __init__(self) -> None:
        self.__reception = Gestion_Reception()
        self.__Simulation_banc = Simulation()
        self.__mon_json = Gestion_json()
        self.__retour_donnees = Gestion_envoi()

    def __prepa_json(self) -> None:
        self.__mon_json.creer_json()
        self.__mon_json.preparation_donnee("temps", self.__Simulation_banc.t)
        self.__mon_json.preparation_donnee("tension",self.__Simulation_banc.u_l)
        self.__mon_json.preparation_donnee("intensite", self.__Simulation_banc.i_l)
        self.__mon_json.charger_json()
        time.sleep(1)

    def __envoi_et_preparation_futur_test(self) -> None:
        self.__retour_donnees.envoi_donnees()
        self.__reception.trame_correct = False
        print("\n")
        self.__mon_json.detruire_json()

    def loop(self) -> None:
        led_pret.off()
        while True:
            led_pret.on()
            
            self.__reception.reception_trame()
            self.__reception.action_trame()

            if self.__reception.trame_correct:

                if self.__reception.action == "SET_CONF":
                    led_pret.off()
                    print("OK;CMD;" + self.__reception.action)
                    self.__Simulation_banc.init_parametre(L=0.330, 
                                                          C=0.5, 
                                                          U0=50, 
                                                          dt=1/self.__reception.parametre_sim[1], 
                                                          nb_step=self.__reception.parametre_sim[0])

                if self.__reception.action == "START":
                    led_pret.off()
                    print("OK;CMD;" + self.__reception.action)
                    self.__Simulation_banc.simulation()

                if self.__reception.action == "STOP":
                    led_pret.off()
                    print("OK;CMD;" + self.__reception.action)
                
                if self.__reception.action == "GET_MEAS":
                    led_pret.off()
                    print("OK;CMD;" + self.__reception.action)

                if self.__reception.action == "GET_STATUS":
                    led_pret.off()
                    print("OK;CMD;" + self.__reception.action)
                    print("simulation prete")

                if self.__reception.action == "RESET":
                    led_pret.off()
                    print("OK;CMD;" + self.__reception.action)
                    machine.reset()
                    break
                    
                if self.__reception.action == "MEAS":
                    led_pret.off()
                    print("OK;CMD;" + self.__reception.action)
                    self.__prepa_json()
                    self.__envoi_et_preparation_futur_test()
                    break
                
                if self.__reception.action == "recevoir\n":
                    led_pret.off()
                    print("OK;CMD;" + self.__reception.action)
                    self.__Simulation_banc.init_parametre(L=0.330, C=0.5, U0=50, dt=1/10, nb_step=50)
                    self.__Simulation_banc.simulation()
                    self.__prepa_json()
                    self.__envoi_et_preparation_futur_test()
                    break

                self.__reception.trame_correct = False
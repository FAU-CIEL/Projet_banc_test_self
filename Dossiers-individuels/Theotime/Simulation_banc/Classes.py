import machine                      # Classe pour la led        # type: ignore 
import select                       # classe detection evenements
import json                         # classe pour le json
import math                         # classe operations mathematiques
import time                         # classe pour le temps
import sys                          # classe systeme (environement + entrée/sortie)
import io                           # classe flux entree/sortie
import os                           # classe systeme (gestion fichiers)
import re                           # classe pour les expressions regulieres


led_pret = machine.Pin(2, machine.Pin.OUT)
LISTE_COMMANDS  = ["SET_CONF", "START", "STOP", "GET_MEAS", "GET_STATUS", "RESET", "MEAS", "recevoir"]

# classe pour la reception des trames de commande/parametrage
class Gestion_Reception:
    def __init__(self) -> None:
        self.__trame = ""
        self.trame_correct = False
        self.action = ""
        self.parametre_sim = [0, 0]
        """
        Premier arg => nb echantillon
        Deuxieme arg => frequence d'echantillonage
        """

    def get_trame(self) -> str:
        return self.__trame

    def __reception_trame(self) -> None:
        self.__trame = ""
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            self.__trame = sys.stdin.readline()
            with open("text.txt", 'a') as f:
                f.write(self.__trame)
            f.close()

    def __chaine_presente(self, commande) -> bool:
        return True if commande in self.__trame else False

    def __decoupage_trame(self) -> None | str:
        if self.__chaine_presente(LISTE_COMMANDS[0]): # SET_CONF
            trame_split = self.__trame.split(";")
            try:
                self.parametre_sim[0] = int(trame_split[1].split('=')[1])
                self.parametre_sim[1] = int(trame_split[2].split('=')[1])
            except ValueError:
                raise "erreur format parametre"

    def __action_trame(self) -> None | str:
        for i in range(len(LISTE_COMMANDS)):
            if self.__chaine_presente(LISTE_COMMANDS[i]):
                self.trame_correct = True
                self.action = LISTE_COMMANDS[i]
                try:
                    self.__decoupage_trame()
                except:
                    raise "erreur format parametre"
                break
            else:
                self.trame_correct = False

    def preparation_trame(self) -> None | str:
        try:
            led_pret.on()
            self.__reception_trame()
            self.__action_trame()
        except:
            raise "erreur format parametre"


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

#classe qui gere les differentes erreurs
class Gestion_erreur:
    def __init__(self):
        self.erreur_present = False
    
    def erreur_trame(self, trame) -> str:
        if not re.search(trame, LISTE_COMMANDS):
            self.erreur_present = True
            return "ERR;1;trame non reconnue"
        
    def erreur_parametre(self) -> str:
        self.erreur_present = True
        return "ERR;2;parametre incorrect"

# classe qui gere les autres fonctions
class Gestion_fonction:
    def __init__(self) -> None:
        self.__reception = Gestion_Reception()
        self.__Simulation_banc = Simulation()
        self.__mon_json = Gestion_json()
        self.__retour_donnees = Gestion_envoi()
        self.__mes_erreurs = Gestion_erreur()

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

    def __set_conf(self) -> None:
        led_pret.off()
        print("OK;CMD;" + self.__reception.action)
        self.__Simulation_banc.init_parametre(L=0.330, 
                                              C=0.5, 
                                              U0=50, 
                                              dt=1/self.__reception.parametre_sim[1], 
                                              nb_step=self.__reception.parametre_sim[0])
        
    def __start(self) -> None:
        led_pret.off()
        print("OK;CMD;" + self.__reception.action)
        self.__Simulation_banc.simulation()

    def __stop(self) -> None:
        led_pret.off()
        print("OK;CMD;" + self.__reception.action)

    def __get_meas(self) -> None:
        led_pret.off()
        print("OK;CMD;" + self.__reception.action)
    
    def __get_status(self) -> None:
        led_pret.off()
        print("OK;CMD;" + self.__reception.action)
        print("simulation prete")

    def __reset(self) -> None:
        led_pret.off()
        print("OK;CMD;" + self.__reception.action)
        machine.reset()
    
    def __meas(self) -> None:
        led_pret.off()
        print("OK;CMD;" + self.__reception.action)
        self.__prepa_json()
        self.__envoi_et_preparation_futur_test()

    def __recevoir(self) -> None:
        led_pret.off()
        print("OK;CMD;" + self.__reception.action)
        self.__Simulation_banc.init_parametre(L=0.330, C=0.5, U0=50, dt=1/10, nb_step=50)
        self.__Simulation_banc.simulation()
        self.__prepa_json()
        self.__envoi_et_preparation_futur_test()
        
    def __gestion_action(self) -> bool:
        if self.__reception.trame_correct:
            if self.__reception.action == LISTE_COMMANDS[0]:
                self.__set_conf()
            elif self.__reception.action == LISTE_COMMANDS[1]:
                self.__start()
            elif self.__reception.action == LISTE_COMMANDS[2]:
                self.__stop()
            elif self.__reception.action == LISTE_COMMANDS[3]:
                self.__get_meas()
            elif self.__reception.action == LISTE_COMMANDS[4]:
                self.__get_status()
            elif self.__reception.action == LISTE_COMMANDS[5]:
                self.__reset()
            elif self.__reception.action == LISTE_COMMANDS[6]:
                self.__meas()
            elif self.__reception.action == LISTE_COMMANDS[7]:
                self.__recevoir()
            self.__reception.trame_correct = False
        if self.__reception.action == LISTE_COMMANDS[5] or self.__reception.action == LISTE_COMMANDS[6] or self.__reception.action == LISTE_COMMANDS[7]:
            return True
        else:            
            return False

    def loop(self) -> None:
        led_pret.off()
        while True:
            try:
                self.__reception.preparation_trame()
            except:
                print(self.__mes_erreurs.erreur_parametre())
                break

            if self.__gestion_action():
                break
            
            if self.__reception.get_trame() != "":
                print(self.__mes_erreurs.erreur_trame(self.__reception.get_trame()))
                break
        
        if self.__mes_erreurs.erreur_present:
            machine.reset()
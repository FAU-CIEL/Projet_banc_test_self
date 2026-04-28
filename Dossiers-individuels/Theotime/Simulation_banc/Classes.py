import machine                      # Classe pour la led        # type: ignore 
import select                       # classe detection evenements
import json                         # classe pour le json
import math                         # classe operations mathematiques
import sys                          # classe systeme (environement + entrée/sortie)
import io                           # classe flux entree/sortie
import os                           # classe systeme (gestion fichiers)


led_pret = machine.Pin(2, machine.Pin.OUT)
LISTE_COMMANDS  = ["SET_CONF", "START", "GET_STATUS", "RESET", "recevoir"]
CHEMIN_JSON = "LOG"
FICHIER_JSON = "donnees_self.json"
C = 0.5 # Capacité du condensateur (F)
L = 0.330 # Inductance de la self (H)
U0 = 50 # Tension initiale (V)

# classe pour la communication
class Communication:
    def __init__(self, chemin_json, fichier_json) -> None:
        self.__mon_json = Gestion_json(chemin_json, fichier_json)
        self.__trame = ""
        self.trame_correct = False
        self.action = ""
        self.parametre_sim = [0, 0] #   Premier arg => nb echantillon   Deuxieme arg => frequence d'echantillonage
        self.__chemin_fichier_json = chemin_json
        self.__fichier_json = fichier_json
        self.__poller = select.poll()
        self.__poller.register(sys.stdout, select.POLLOUT)

    def get_trame(self) -> str:
        return self.__trame
    
    def __reception_trame(self) -> None:
        self.__trame = ""
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            self.__trame = sys.stdin.readline()
            with open("text.txt", 'a') as f:
                f.write(self.__trame)
            f.close()

    def __decoupage_trame(self) -> None | Exception:
        if LISTE_COMMANDS[0] in self.__trame: # SET_CONF
            trame_split = self.__trame.split(";")
            try:
                self.parametre_sim[0] = int(trame_split[1].split('=')[1])
                self.parametre_sim[1] = float(trame_split[2].split('=')[1])
            except Exception:
                raise Exception("erreur format parametre")
            
    def __action_trame(self) -> None | Exception:
        for i in range(len(LISTE_COMMANDS)):
            if LISTE_COMMANDS[i] in self.__trame:
                self.trame_correct = True
                self.action = LISTE_COMMANDS[i]
                try:
                    self.__decoupage_trame()
                except Exception as e:
                    raise Exception(e)
                break
            else:
                self.trame_correct = False
    
    def preparation_trame(self) -> None | Exception:
        try:
            led_pret.on()
            self.__reception_trame()
            self.__action_trame()
        except Exception as e:
            raise Exception(e)

    def __fichier_existant(self) -> bool:
        if sys.platform == "esp32":
            os.chdir("/" + self.__chemin_fichier_json)
            for fichier in os.ilistdir():
                nom_fichier, type_, *_ = fichier
                if type_ == 0x8000 and nom_fichier == self.__fichier_json: # type 0x8000 = fichier
                    return True
        return False
    
    def __sortie_prete(self) -> bool:
        events = self.__poller.poll()
        for obj, event in events:
            if event == select.POLLOUT:
                return True
            else:
                return False
    
    def envoi_donnees(self) -> None | Exception:
        try:
            if self.__sortie_prete() and self.__fichier_existant():
                with io.open(self.__fichier_json, 'r') as file:
                    for line in file:
                        print(line.strip())
                file.close()
        except Exception:
            raise Exception("erreur de memoire")
    
    def remplir_json(self, temps, tension, intensite) -> None:
        self.__mon_json.prepa_json(temps, tension, intensite)
    
    def detruire_json(self) -> None:
        self.__mon_json.detruire_json()

# classe qui simule le circuit (equa diff + transformer en Z)
class Simulation:
    def __init__(self) -> None:
        # parametre physique
        self.__L = L
        self.__C = C

        # condition initial
        self.__U0 = U0

        # gestion du temps
        self.__n_steps = 0  # nb d'etapes
        self.__dt = 0       # pas de temps
        
        self.__omega0 = 1 / math.sqrt(self.__L * self.__C)
        self.__phi = 0

        # tableaux de sorties
        self.t = []
        self.u_l = []
        self.i_l = []

    def init_parametre(self, nb_step, dt) -> None:
        self.__n_steps = nb_step
        self.__dt = dt

        self.t = [0] * self.__n_steps
        self.u_l = [0] * self.__n_steps
        self.i_l = [0] * self.__n_steps

    def get_dt(self) -> float:
        return self.__dt
    
    def get_n_steps(self) -> int:
        return self.__n_steps

    def __calcul_tension(self, t) -> float:
        return self.__U0 * math.cos(self.__omega0 * t + self.__phi)

    def __calcul_intensite(self, t) -> float:
        return self.__C * self.__U0 * math.sin(self.__omega0 * t)

    def __transformer_Z_tension(self, z) -> float:
        return self.__U0 * ((z**2 - z * math.cos(self.__omega0)) / (z**2 - 2 * z * math.cos(self.__omega0) + 1))

    def __transformer_Z_intensite(self, z) -> float:
        return self.__C * self.__U0 * self.__omega0 * ((z * math.sin(self.__omega0)) / (z ** 2 -2 * z * math.cos(self.__omega0) + 1))

    def simulation(self) -> None:
        for n in range(self.__n_steps):
            t = self.__dt * n
            self.t[n] = t
            self.u_l[n] = self.__transformer_Z_tension(t)
            self.i_l[n] = self.__transformer_Z_intensite(t)

# classe qui stocke les valeurs dans un json
class Gestion_json:
    def __init__(self, chemin_json, fichier_json) -> None:
        self.__chemin_json = chemin_json
        self.__fichier_json = fichier_json
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

    def __creer_json(self) -> None:
        if sys.platform == "esp32":
            self.__creer_chemin_json()
            os.chdir(self.__chemin_json)
            io.open(self.__fichier_json, 'w')

    def __preparation_donnee(self, donnee, valeur) -> None:
        self.__donner_a_stocker[donnee] = valeur

    def __charger_json(self) -> None:
        with io.open(self.__fichier_json) as file:
            json.dump(self.__donner_a_stocker, file)
        file.close()

    def prepa_json(self, temps, tension, intensite) -> None:
        self.__creer_json()
        self.__preparation_donnee("temps", temps)
        self.__preparation_donnee("tension", tension)
        self.__preparation_donnee("intensite", intensite)
        self.__charger_json()

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

#classe qui gere les differentes erreurs
class Gestion_erreur:
    def __init__(self):
        self.erreur_present = False

    def erreur_trame(self, trame) -> None | str:
        for cmd in LISTE_COMMANDS:
            if cmd in trame:
                return None
        self.erreur_present = True
        return "ERR;1;trame non reconnue"

    def erreur_parametre(self) -> str:
        self.erreur_present = True
        return "ERR;2;parametre incorrect"

    def erreur_memoire(self) -> str:
        self.erreur_present = True
        return "ERR;3;erreur de memoire"

# classe qui gere les autres fonctions
class Gestion_fonction:
    def __init__(self) -> None:
        self.__communication = Communication(CHEMIN_JSON, FICHIER_JSON)
        self.__Simulation_banc = Simulation()
        self.__mes_erreurs = Gestion_erreur()

    def __envoi_et_preparation_futur_test(self) -> None | Exception:
        try:
            self.__communication.envoi_donnees()
            self.__communication.trame_correct = False
            print("\n")
            self.__communication.detruire_json()
        except Exception as e:
            self.__communication.detruire_json()
            raise Exception(e)

    def __set_conf(self) -> None:
        led_pret.off()
        self.__Simulation_banc.init_parametre(nb_step=self.__communication.parametre_sim[0],
                                              dt=1/self.__communication.parametre_sim[1])
        print("OK;CMD;" + self.__communication.action)

    def __start(self) -> None | Exception:
        led_pret.off()
        self.__Simulation_banc.simulation()
        try:
            self.__communication.remplir_json(self.__Simulation_banc.t, self.__Simulation_banc.u_l, self.__Simulation_banc.i_l)
            self.__envoi_et_preparation_futur_test()
            print("\n")
            print("OK;CMD;" + self.__communication.action)
        except Exception as e:
            raise Exception(e)

    def __get_status(self) -> None:
        led_pret.off()
        valeur_simulation = f"Parametre;nb_echantillon={self.__Simulation_banc.get_n_steps()};frequence_echantillonage={1/self.__Simulation_banc.get_dt()}"
        print(valeur_simulation)
        print("simulation prete")
        print("OK;CMD;" + self.__communication.action)

    def __reset(self) -> None:
        led_pret.off()
        print("OK;CMD;" + self.__communication.action)
        machine.reset()
   
    def __recevoir(self) -> None:
        led_pret.off()
        self.__Simulation_banc.init_parametre(nb_step=50, dt=1/10)
        self.__Simulation_banc.simulation()
        self.__communication.remplir_json(self.__Simulation_banc.t, self.__Simulation_banc.u_l, self.__Simulation_banc.i_l)
        self.__envoi_et_preparation_futur_test()
        print("OK;CMD;" + self.__communication.action)

    def __gestion_action(self) -> bool | Exception:
        if self.__communication.trame_correct:
            try:
                if self.__communication.action == LISTE_COMMANDS[0]:
                    self.__set_conf()
                    return False
                elif self.__communication.action == LISTE_COMMANDS[1]:
                    self.__start()
                    return True
                elif self.__communication.action == LISTE_COMMANDS[2]:
                    self.__get_status()
                    return False
                elif self.__communication.action == LISTE_COMMANDS[3]:
                    self.__reset()
                    return True
                elif self.__communication.action == LISTE_COMMANDS[4]:
                    self.__recevoir()
                    return True
                self.__communication.trame_correct = False
                self.__communication.action = ""
            except Exception as e:
                raise Exception(e)

    def loop(self) -> None:
        led_pret.off()
        while True:
            try:
                self.__communication.preparation_trame()
                if self.__gestion_action():
                    return

            except Exception as e:
                if str(e) == "erreur format parametre":
                    print(self.__mes_erreurs.erreur_parametre())
                    break
                elif str(e) == "erreur de memoire":
                    print(self.__mes_erreurs.erreur_memoire())
                    break

            if self.__communication.get_trame() != "":
                erreur = self.__mes_erreurs.erreur_trame(self.__communication.get_trame())
                if erreur and self.__mes_erreurs.erreur_present:
                    print(erreur)
                    break

        if self.__mes_erreurs.erreur_present:
            machine.reset()
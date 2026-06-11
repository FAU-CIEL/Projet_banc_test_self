import machine                      # Classe pour la led        # type: ignore 
import select                       # classe detection evenements
import json                         # classe pour le json
import math                         # classe operations mathematiques
import sys                          # classe systeme (environement + entrée/sortie)
import gc                           # classe pour la gestion de la memoire (HEAP)
import io                           # classe flux entree/sortie
import os                           # classe systeme (gestion fichiers)


led_pret = machine.Pin(2, machine.Pin.OUT)
LISTE_COMMANDS  = ["SET_CONF", "START", "GET_STATUS", "RESET", "SET_IND", "recevoir"]
FICHIER_JSON = "donnees_self.json"
C = 0.000001 # Capacité du condensateur (F)
L = 0.0001 # Inductance de la self (H)
U0 = 50 # Tension initiale (V)
FICHIER_DE_SAUVEGARDE = "sauvegarde.txt"
UNITE_FREQUENCE_POSSIBLE = [("Hz\n", 1), ("kHz\n", 1_000), ("MHz\n", 1_000_000), ("GHz\n", 1_000_000_000)]

POUR_ER = False     # variable pour difinir si l'esp est pour les ER ou non (moins de fonctionnalité pour les ER)

# classe pour la communication
class Communication:
    def __init__(self, fichier_json) -> None:
        self.__mon_json = None
        self.__trame = ""
        self.trame_correct = False
        self.action = ""
        self.parametre_sim = [0, 0]         # Premier arg => nb echantillon   Deuxieme arg => frequence d'echantillonage
        self.multiplicateur_frequence = 1_000_000   # multiplicateur de la frequence d'echantillonage (Hz, kHz, MHz, GHz)
        self.inductance = 1                 # nouvelle inductance definit sur commande
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
                if not POUR_ER:
                    for unite, multiplicateur in UNITE_FREQUENCE_POSSIBLE:
                        if trame_split[3] == unite:
                            self.multiplicateur_frequence = multiplicateur
                            self.parametre_sim[1] *= multiplicateur
                            break
            except Exception:
                raise Exception("erreur format parametre")
        elif LISTE_COMMANDS[4] in self.__trame: # SET_IND
            trame_split = self.__trame.split(";")
            try:
                self.inductance = float(trame_split[1])
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
    
    def __sortie_prete(self) -> bool:
        events = self.__poller.poll()
        for obj, event in events:
            if event == select.POLLOUT:
                return True
            else:
                return False
    
    def envoi_donnees(self) -> None | Exception:
        try:
            if self.__fichier_json in os.listdir() and self.__sortie_prete():
                with io.open(self.__fichier_json, 'r') as file:
                    for line in file:
                        sys.stdout.write(line.strip() + "\n")
                file.close()
        except Exception:
            raise Exception("erreur de memoire")
    
    def remplir_json(self, temps, tension, intensite) -> None:
        self.__mon_json = Gestion_json(self.__fichier_json)
        self.__mon_json.prepa_json(temps, tension, intensite)
    
    def detruire_json(self) -> None:
        self.__mon_json.detruire_json()
        del self.__mon_json
        gc.collect()

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

    def init_parametre(self, *args) -> None:
        if len(args) == 2:
            self.__n_steps = args[0]
            self.__dt = args[1]

            self.t = [0] * self.__n_steps
            self.u_l = [0] * self.__n_steps
            self.i_l = [0] * self.__n_steps

        elif len(args) == 1:
            self.__L = args[0]
            self.__omega0 = 1 / math.sqrt(self.__L * self.__C)

    def get_dt(self) -> float:
        return self.__dt
    
    def get_n_steps(self) -> int:
        return self.__n_steps
    
    def get_L(self) -> float:
        return self.__L

    def __calcul_tension(self, t) -> float:
        return self.__U0 * math.cos(self.__omega0 * t + self.__phi)

    def __calcul_intensite(self, t) -> float:
        return self.__C * self.__U0 * self.__omega0 * math.sin(self.__omega0 * t)

    def __transformer_Z_tension(self, z) -> float: # fonction inutile
        return self.__U0 * ((z**2 - z * math.cos(self.__omega0)) / (z**2 - 2 * z * math.cos(self.__omega0) + 1))

    def __transformer_Z_intensite(self, z) -> float: # fonction inutile
        return self.__C * self.__U0 * self.__omega0 * ((z * math.sin(self.__omega0)) / (z**2 - 2 * z * math.cos(self.__omega0) + 1))

    def simulation(self) -> None:
        for n in range(self.__n_steps):
            t = self.__dt * n
            self.t[n] = t
            self.u_l[n] = self.__calcul_tension(t)
            self.i_l[n] = self.__calcul_intensite(t)

# classe qui stocke les valeurs dans un json
class Gestion_json:
    def __init__(self, fichier_json) -> None:
        self.__fichier_json = fichier_json
        self.__donner_a_stocker = {
            "temps": [],
            "tension": [],
            "intensite": []
            }

    def __creer_json(self) -> None:
        if sys.platform == "esp32":
            with io.open(self.__fichier_json, 'w') as creation_file:
                pass
            creation_file.close()

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

    def detruire_json(self) -> None:
        if sys.platform == "esp32":
            if self.__fichier_json in os.listdir():
                os.remove(self.__fichier_json)

#classe qui gere les differentes erreurs
class Gestion_erreur:
    def __init__(self):
        self.erreur_present = False

    def erreur_trame(self, trame) -> None | str:
        for cmd in LISTE_COMMANDS:
            if cmd in trame:
                return None
        self.erreur_present = True
        return "ERR;1;trame non reconnue\n"

    def erreur_parametre(self) -> str:
        self.erreur_present = True
        return "ERR;2;parametre incorrect\n"

    def erreur_memoire(self) -> str:
        self.erreur_present = True
        return "ERR;3;erreur de memoire\n"

# classe qui gere les autres fonctions
class Gestion_fonction:
    def __init__(self) -> None:
        self.__communication = Communication(FICHIER_JSON)
        self.__Simulation_banc = Simulation()
        self.__mes_erreurs = Gestion_erreur()
        self.__charger_sauvegarde()

    def __envoi_et_preparation_futur_test(self) -> None | Exception:
        try:
            self.__communication.envoi_donnees()
            self.__communication.trame_correct = False
            sys.stdout.write("\n")
            self.__communication.detruire_json()
        except Exception as e:
            self.__communication.detruire_json()
            raise Exception(e)

    def __set_conf(self) -> None:
        led_pret.off()
        self.__Simulation_banc.init_parametre(self.__communication.parametre_sim[0],
                                              1/self.__communication.parametre_sim[1])
        sys.stdout.write("OK;CMD;" + self.__communication.action + "\n")

    def __start(self) -> None | Exception:
        led_pret.off()
        self.__Simulation_banc.simulation()
        try:
            self.__communication.remplir_json(self.__Simulation_banc.t, self.__Simulation_banc.u_l, self.__Simulation_banc.i_l)
            self.__envoi_et_preparation_futur_test()
            sys.stdout.write("\n")
            sys.stdout.write("OK;CMD;" + self.__communication.action + "\n")
        except Exception as e:
            raise Exception(e)

    def __get_status(self) -> None:
        led_pret.off()
        dt = self.__Simulation_banc.get_dt()
        nb_step = self.__Simulation_banc.get_n_steps()
        indu = self.__Simulation_banc.get_L()
        unite_frequence = ""
        if not POUR_ER:
            for unite, multiplicateur in UNITE_FREQUENCE_POSSIBLE:
                if self.__communication.multiplicateur_frequence == multiplicateur:
                    unite_frequence = unite
                    break
        valeur_simulation = ""
        if dt != 0:
            if POUR_ER:
                valeur_simulation = "Parametre;nb_echantillon=" + str(nb_step) + ";frequence_echantillonage=" + str((1/dt)) + "\n"
            else:
                valeur_simulation = "Parametre;nb_echantillon=" + str(nb_step) + ";frequence_echantillonage=" + str((1/dt) / self.__communication.multiplicateur_frequence) + unite_frequence
        else:
            valeur_simulation = "Parametre;nb_echantillon=" + str(nb_step) + ";frequence_echantillonage=0Hz\n"
        sys.stdout.write(valeur_simulation)
        sys.stdout.write("inductance=" + str(indu) + "\n")
        sys.stdout.write("simulation prete\n")
        sys.stdout.write("OK;CMD;" + self.__communication.action + "\n")

    def __reset(self) -> None:
        led_pret.off()
        sys.stdout.write("OK;CMD;" + self.__communication.action + "\n")
        machine.reset()
    
    def __set_ind(self) -> None:
        led_pret.off()
        self.__Simulation_banc.init_parametre(self.__communication.inductance)
        sys.stdout.write("OK;CMD;" + self.__communication.action + "\n")
   
    def __recevoir(self) -> None:
        led_pret.off()
        self.__Simulation_banc.init_parametre(50, 1/10)
        self.__Simulation_banc.simulation()
        self.__communication.remplir_json(self.__Simulation_banc.t, self.__Simulation_banc.u_l, self.__Simulation_banc.i_l)
        self.__envoi_et_preparation_futur_test()
        sys.stdout.write("OK;CMD;" + self.__communication.action + "\n")

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
                    self.__set_ind()
                    return False
                elif self.__communication.action == LISTE_COMMANDS[5]:
                    self.__recevoir()
                    return True
                self.__communication.trame_correct = False
                self.__communication.action = ""
            except Exception as e:
                raise Exception(e)
            
    def __mon_reset(self) -> None:
        if self.__Simulation_banc.get_n_steps() != 0 and self.__Simulation_banc.get_dt() != 0:
            with io.open(FICHIER_DE_SAUVEGARDE, 'w') as save_file:
                if POUR_ER:
                    save_file.write("nb_enchantillon=" + str(self.__Simulation_banc.get_n_steps()) +
                                    ";frequence_echantillonage=" + str(1/self.__Simulation_banc.get_dt()) +
                                    ";inductance=" + str(self.__Simulation_banc.get_L()))
                else:
                    save_file.write("nb_enchantillon=" + str(self.__Simulation_banc.get_n_steps()) + 
                                    ";frequence_echantillonage=" + str(1/self.__Simulation_banc.get_dt()) + 
                                    ";inductance=" + str(self.__Simulation_banc.get_L()) + 
                                    ";multiplicateur_frequence=" + str(self.__communication.multiplicateur_frequence))
            save_file.close()
        
        if self.__mes_erreurs.erreur_present:
            machine.reset()
        else:
            del self.__Simulation_banc
            gc.collect()

    def __charger_sauvegarde(self) -> None:
        if FICHIER_DE_SAUVEGARDE in os.listdir():
            with io.open(FICHIER_DE_SAUVEGARDE, 'r') as save_file:
                if POUR_ER:
                    parametres = save_file.readline().split(";")
                    nb_echantillon = int(parametres[0].split("=")[1])
                    frequence_echantillonage = float(parametres[1].split("=")[1])
                    inductance = float(parametres[2].split("=")[1])
                    self.__Simulation_banc.init_parametre(nb_echantillon, 1/frequence_echantillonage)
                    self.__Simulation_banc.init_parametre(inductance)
                else:
                    parametres = save_file.readline().split(";")
                    nb_echantillon = int(parametres[0].split("=")[1])
                    frequence_echantillonage = float(parametres[1].split("=")[1])
                    inductance = float(parametres[2].split("=")[1])
                    multiplicateur_frequence = int(parametres[3].split("=")[1])
                    self.__Simulation_banc.init_parametre(nb_echantillon, 1/frequence_echantillonage)
                    self.__Simulation_banc.init_parametre(inductance)
                    self.__communication.multiplicateur_frequence = multiplicateur_frequence
            save_file.close()
            os.remove(FICHIER_DE_SAUVEGARDE)

    def loop(self) -> None:
        led_pret.off()
        while True:
            try:
                self.__communication.preparation_trame()
                if self.__gestion_action():
                    break

            except Exception as e:
                if str(e) == "erreur format parametre":
                    sys.stdout.write(self.__mes_erreurs.erreur_parametre())
                    break
                elif str(e) == "erreur de memoire":
                    sys.stdout.write(self.__mes_erreurs.erreur_memoire())
                    break

            if self.__communication.get_trame() != "":
                erreur = self.__mes_erreurs.erreur_trame(self.__communication.get_trame())
                if erreur and self.__mes_erreurs.erreur_present:
                    sys.stdout.write(erreur)
                    break

        self.__mon_reset()
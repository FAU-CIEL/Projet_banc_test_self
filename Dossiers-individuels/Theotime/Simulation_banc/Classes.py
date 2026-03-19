import select   # classe detection evenements
import errno    # classe erreurs
import math     # classe operations mathematiques
import sys      # classe systeme (environement + entrée/sortie)
import io       # classe flux entree/sortie
import os       # classe systeme (gestion fichiers)


# classe pour la reception des trames de commande/parametrage
class Gestion_Reception:
    def __init__(self):
        self.__trame = ""

    def reception_trame(self):
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            self.__trame = sys.stdin.readline()

    def gestion_trame(self):
        pass

# classe qui simule le circuit (equa diff + transformer en Z)
class Simulation:
    def __init__(self, L, C, U0, dt, duree):
        # parametre physique
        self.__L = L
        self.__C = C

        # condition initial
        self.__U0 = U0

        # gestion du temps
        self.__dt = dt                                                    # pas de temps
        self.__duree = duree                                              # temps de sim
        self.__n_steps = int(max(1, math.ceil(self.__duree / self.__dt)))     # nb d'etapes

        self.__omega0 = 1/math.sqrt(self.__L * self.__C)
        self.__f0 = self.__omega0 * self.__dt
        self.__phi = 0

        # tableaux de sorties
        self.t = []
        self.i_l = []
        self.u_l = []

    def __calcul_tension(self, t):
        return self.__U0 * math.cos(self.__omega0 * t + self.__phi)
    
    def __calcul_intensite(self, t):
        return -self.__C * self.__U0 * self.__omega0 * math.sin(self.__omega0 * t)

    def __transformer_Z_tension(self, z):
        return self.__U0 * (z * (z * math.cos(self.__phi - math.cos(self.__f0 - self.__phi))) / z **2 - 2 * z * math.cos(self.__f0) + 1)

    def __transformer_Z_intensite(self, z):
        return -self.__C * self.__U0 * self.__omega0 * (z * math.sin(self.__f0) / z **2 - 2 * z * math.cos(self.__f0) + 1)
    
    def simulation(self):
        for N in range(self.__n_steps):
            self.t.append(self.__dt * N)
            self.i_l.append(self.__transformer_Z_intensite(self.t[N]))
            self.u_l.append(self.__transformer_Z_tension(self.t[N]))


# classe qui stocke les valeurs dans un json
# classe terminer!! et fonctionnelle
class Gestion_json:
    def __init__(self):
        self.__chemin_json = "LOG"
        self.__fichier_json = "donnees_self.json"
        self.__donner_a_stocker = "{"

    def __dossier_existant(self):
        for dossier in os.ilistdir():
            nom_dossier, type_, *_ = dossier
            if type_ == 0x4000 and nom_dossier == self.__chemin_json:  # type 0x4000 = dossier
                return True
        return False
    
    def __creer_chemin_json(self):
        if not self.__dossier_existant():
            os.mkdir(self.__chemin_json)
    
    def creer_json(self):
        if sys.platform == "esp32":
            self.__creer_chemin_json()
            os.chdir(self.__chemin_json)
            try:
                io.open(self.__fichier_json, 'x')
            except errno.EEXIST:
                io.open(self.__fichier_json, 'w')

    def preparation_donnee(self, donnee, valeur):
        if donnee == "temps":
            self.__donner_a_stocker += "\n\"temps\": \n\""
        if donnee == "tension":
            self.__donner_a_stocker += "\n\"tension\": \n\""
        if donnee == "intensiter":
            self.__donner_a_stocker += "\n\"intensite\": \n\""
        for n in range(len(valeur)):
            self.__donner_a_stocker += f"{str(valeur[n])}," if n != len(valeur)-1 else f"{str(valeur[n])}\",\n"
        if donnee == "intensiter":
            self.__donner_a_stocker = self.__donner_a_stocker[:-2]
            self.__donner_a_stocker += "\n}"
    
    def charger_json(self):
        with io.open(self.__fichier_json, 't') as file:
            file.write(self.__donner_a_stocker)
        file.close()

# classe qui renvoie les données a l'IHM
class Gestion_envoi:
    def __init__(self):
        self.__chemin_fichier_json = "LOG"
        self.__fichier_json = "donnees_self.json"

    def __fichier_existant(self):
        while os.getcwd() != "/": os.chdir("..") # permet de revenir a la racine

        os.chdir(self.__chemin_fichier_json)
        for fichier in os.ilistdir():
            nom_fichier, type_, *_ = fichier
            if type_ == 0x8000 and nom_fichier == self.__fichier_json: # type 0x8000 = fichier
                return True
        return False

    def __sortie_prete(self):
        poller = select.poll()
        poller.register(sys.stdout, select.POLLOUT)
        events = poller.poll()
        for obj, event in events:
            if event == select.POLLOUT:
                return True
            else:
                return False

    def envoi_donnees(self):
        if self.__sortie_prete():
            with io.open(self.__fichier_json, 'r') as file:
                for line in file:
                    sys.stdout.write(line.strip() + "\n")

# classe qui gere les autres fonctions
class Gestion_fonction:
    def __init__(self):
        self.reception = Gestion_Reception()
        self.Simulation_banc = Simulation(0, 0, 0, 0, 0)
        self.mon_json = Gestion_json()
        self.retour_donnees = Gestion_envoi()

    def loop(self):
        self.mon_json.creer_json()
        self.mon_json.preparation_donnee("temps", self.Simulation_banc.t)
        self.mon_json.preparation_donnee("tension",self.Simulation_banc.u_l)
        self.mon_json.preparation_donnee("intensiter", self.Simulation_banc.i_l)
        self.mon_json.charger_json()
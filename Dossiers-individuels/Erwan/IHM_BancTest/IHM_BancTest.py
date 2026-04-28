# ============================================================
# @file    IHM_BancTest.py
# @brief   Simulateur graphique de banc de test électrique
# @author  Leroux Erwan
# @version 2.0
# ============================================================

# ============================================================
# IMPORTS
# ============================================================
import tkinter as tk
from tkinter import VERTICAL, ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import sys
import json
import sqlite3
from numpy import column_stack, delete
import serial
import serial.tools.list_ports
import pandas as pd
from datetime import datetime
import re
import time

# ============================================================
# INITIALISATION DE LA FENÊTRE PRINCIPALE
# ============================================================

IHM = tk.Tk()
IHM.title("Interface Banc de Test")
IHM.geometry("1600x700")
L_commande = ["SET_CONF","START\n","RESET\n","GET_STATUS\n","recevoir\n"]
# ------------------------------------------------------------
# INITIALISATION DES CLASSES 
# ------------------------------------------------------------

# ============================================================
# FONCTIONS DETECTION ESP32
# ============================================================
class CGestion_Connexion :
    def __init__(self):
            self.ser=None
            self.donnees=[]
            self.compteur= 0
    def detecter_esp32(self):
        ## @fonc detecter_esp32
        # Verification de la connexion entre l'ESP32 et l'IHM
        #Le programme va rechercher dans les ports COM si l'un d'entre eux possèdent en description "CP210" "ESP32" "USB Serial" "USB UART" afin de se connecter
        

        ports = serial.tools.list_ports.comports()

        for port in ports:
            if "CP210" in port.description or "USB Serial" in port.description or "ESP32" in port.description or "USB UART" in port.description :
                try:
                    self.ser = serial.Serial(port.device,115200)

                    print("ESP32 connecté sur:",port.device)
                   

                    return
                except:
                    pass

        print("ESP32 non détecté")
    def envoie_parametre(self) :
        gestion_limite=CGestion_Limite()


        texte_status.config(state="normal")
        texte_status.insert("end", "Paramètre enregistré\n")
        texte_status.insert(tk.END,f"Nombre echantillons:  {gestion_limite.Nb_Ech.get()}\n")
        texte_status.insert(tk.END,f"Fréquence Echantillonnage: {gestion_limite.Feq.get()} \n")
        texte_status.see("end")
        texte_status.config(state="disabled")

        trame = ""

        Ech=gestion_limite.Nb_Ech.get()
        Feq=gestion_limite.Feq.get()
        #Verification que la commande param est reçue et attend de recevoir OK;CMD pour continuer le programme
        param=L_commande[0]+ ";N="+Ech + ";" +"F="+Feq +"\n"
        print(param)
        if self.ser is not None:
            self.ser.write(param.encode())
            
            while not re.search("OK;CMD", trame):
                trame = self.ser.readline().decode().strip()
                if re.search("ERR;", trame):
                    print("erreur")
                    break
         
        else:
            print("ESP32 non connecté")

    def recup_info(self):
        
        self.donnees = []
        self.compteur= 0
        
        self.ser.write(L_commande[1].encode())
        
        while True:
            valeur_json=self.ser.readline().decode().strip()
            
            print(valeur_json if not "" else "rien")
            if valeur_json:
                if re.search(re.escape('{'),str(valeur_json)):
                    donnee=json.loads(valeur_json)

                    print(donnee)

                    break
        self.val_temps = donnee["temps"]
        self.val_tens = donnee["tension"]
        self.val_intensite = donnee["intensite"]
        return self.val_temps , self.val_tens , self.val_intensite

    def reinitialiser(self):
        ## @var reinitialiser
        #  Suppression de toutes les données du tableau/graphique et des paramètres de mesures
        self.ser.write(L_commande[2].encode())
        
        tableau.delete(*tableau.get_children())
        ax.clear()
        graph.draw()
    def demarrer_mesure(self):
        
        ## @var demarrer_mesure
        #  Recupération et affichage des paramètres choisis pour le test 
        t,tens,inten=self.recup_info()
        ech=1
       
                    

        for i in range (len(t)):
           tableau.insert("", "end", values=(ech, tens[i],inten[i],inten[i]/t[1],t[i]))
           ech+=1
        gestion_fonction = CGestion_Graphique()
        gestion_fonction.graphique()

# ============================================================
# FONCTIONS DE GESTION DES FICHIERS CSV
# ============================================================
class CGestion_Fichier_CSV :
    ## @class CGestion_Fichier_CSV
    #  Classe pour la gestion des fonctions pour les fichiers CSV

    def sauvegarder_csv(self):
        ## @var sauvegarder_csv
        # Récupération des données sur L'IHM pour les sauvegarder dans un tableau en csv
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerow(["Echantillon", "Inductance","Tension [v]","Intensite [A]","Temps [s]"])

                for item in tableau.get_children():
                    writer.writerow(tableau.item(item, "values"))

            messagebox.showinfo("Succès", f"Données sauvegardées dans :\n{filepath}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur de sauvegarde :\n{e}")


    def charger_csv(self):
        ## @var charger_csv
        # Ouvrir un fichier en csv pour recupérer les données et les afficher dans le tableau et graphiquement
        filepath = filedialog.askopenfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not filepath:
            return

        try:
            tableau.delete(*tableau.get_children())

            with open(filepath, mode="r", newline="", encoding="utf-8") as file:
                reader = csv.reader(file, delimiter=";")
                next(reader)  # ignore l'en-tête

                for row in reader:
                    tableau.insert("", "end", values=row[:5])

            gestion_graphique = CGestion_Graphique()
            gestion_graphique.graphique()
            messagebox.showinfo("Succès", f"Données chargées depuis :\n{filepath}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur de chargement :\n{e}")
class CGestion_Fonction:
    ## @class CGestion_Fonction
    #  Classe pour la gestion des fonctions quitter et information avec l'interface pour la recherche dans l'historique
    
    # ============================================================
    # FONCTIONS DE CONTRÔLE
    # ============================================================
    def __init__(self):
            self.HIST=None
    def quitter(self):
        IHM.destroy()
        sys.exit()

    
    
    # ============================================================
    # FONCTION INFORMATION
    # ============================================================
    def information(self):
    
        ## @var information
        #  Message pour le bouton information
        messagebox.showinfo("A propos","Interface Homme Machine \n Developpé par Leroux Erwan \n Version 2.0")

    # ============================================================
    # FONCTION HISTORIQUE
    # ============================================================
    def historique(self):
        detection_esp32=CGestion_Connexion()
        t,tens,inten= detection_esp32.recup_info()
        
        if self.HIST is None or not self.HIST.winfo_exists(): 
               self.HIST = tk.Tk()
               self.HIST.title("Historique")
               self.HIST.geometry("700x400")
               partie_historique = ttk.LabelFrame(self.HIST, text="Historique")
               partie_historique.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
               partie_historique.columnconfigure(0, weight=2)
               partie_historique.rowconfigure(0, weight=2)
               partie_historique.rowconfigure(1, weight=2)
               # ----- Table -----
               table = ttk.Treeview(
                   partie_historique,
                   columns=("E", "I","T"),
                   show="headings",
                   height=8
               )
               table.heading("E", text="Echantillon")
               table.heading("I", text="Inductance")
               table.heading("T", text="Temps [s]")
               table.grid(row=1, column=0, sticky="nsew")
               for i in range (len(t)):
                    table.insert("", "end", values=(detection_esp32.ech, detection_esp32.tens[i],detection_esp32.t[i]))
                    ech+=1    

     # ============================================================
    # FONCTION BASE DE DONNEE
    # ============================================================
class CGestion_BDD:
     ## @class CGestion_BDD
     #  Classe pour la gestion des fonctions en lien avec la base de donnée
    
    def __init__(self):
        self.Nom_Test =""
        self.Date =""
        self.Nom_Tech= ""
        self.BDD=None
        self.Impedance = 0
        self.Echantillon = 0
        self.Temps = 0
        # ============================================================
        # FONCTION BASE DE DONNEE
        # ============================================================
    def creer_BDD(self):
           ## @var creer_BDD
           #@brief Création de l'IHM pour la Base de Donnée avec ses fonctionnalitées
           
           if self.BDD is None or not self.BDD.winfo_exists(): 
               self.BDD = tk.Toplevel()
               self.BDD.title("Base de Donnée")
               self.BDD.geometry("400x200")
               frame_gauche = ttk.Frame(self.BDD)
               frame_gauche.grid(row=0, column=0, sticky="n", padx=75, pady=20)
               frame_gauche.columnconfigure(0, weight=1)
               partie_bdd = ttk.LabelFrame(frame_gauche, text="Création Test")
               partie_bdd.grid(row=4, column=0, sticky="nw", pady=1)
               partie_bdd.columnconfigure(0, weight=1)
               partie_bdd.columnconfigure(1, weight=1)
               ttk.Label(partie_bdd, text="Entrer le nom du test").grid(row=0, column=0, sticky="w", padx=5, pady=2)
               self.Nom_Test = ttk.Entry(partie_bdd)
               self.Nom_Test.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
               ttk.Label(partie_bdd, text="Date").grid(row=1, column=0, sticky="w", padx=5, pady=2)
               self.Date = ttk.Entry(partie_bdd)
               self.Date.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
               ttk.Label(partie_bdd, text="Nom Technicien").grid(row=2, column=0, sticky="w", padx=5, pady=2)
               self.Nom_Tech = ttk.Entry(partie_bdd)
               self.Nom_Tech.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
           
               bouton_Creer = ttk.Button(partie_bdd, text="Ajouter",command=gestion_bdd.rsql)
               bouton_Creer.grid(row=3, column=0, pady=5)
           
       
    def rsql(self):
           ## @var RSQL
           #@brief Création de la Base de Donnée avec une requête SQL
            
            gestion_bdd = CGestion_BDD()
            conn = sqlite3.connect("Base_Projet.db")
            cursor = conn.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Test (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Nom_Test TEXT,
                Date TEXT,
                Nom_Tech TEXT,
                Echantillon INT,
                Inductance FLOAT,
                Temps FLOAT
            )
            """)

            cursor.execute(
                "INSERT INTO Test (Nom_Test, Date, Nom_Tech) VALUES (?, ?, ?)",
                (
                    self.Nom_Test.get(),
                    self.Date.get(),
                    self.Nom_Tech.get()
                )
            )

            conn.commit()
            conn.close()

            print("Le Test a été enregistré !")
    def ajout_BDD(self):

        ## @var conn
        #@brief Connexion de l'interface a la base donnée afin de transférer des données
        conn = sqlite3.connect("Base_Projet.db")
        cursor = conn.cursor()
        ## @var requete
        #@brief Création d'une requete pour inserer dans la table les valeurs des echantillons ,l'impédance , le temps
        requete="INSERT INTO Test (Echantillon,Inductance, Temps) VALUES (?, ?, ?)"
        for valeur in tableau.get_children():
            ligne = tableau.item(valeur, "values")
            cursor.execute(requete,(ligne[0],ligne[3],ligne[4]))
        conn.commit()
        conn.close()

# ============================================================
# FONCTION GRAPHIQUE
# ============================================================
class CGestion_Graphique:
    def __init__(self):
        self.x = []
        self.y = []

    def graphique(self):
        self.x = []
        self.y = []
        self.yi= []
        self.yimp= []
        
        ax.clear()

        
        for item in tableau.get_children():
        ## @var valeurs
        #@brief Renvoie aux données dans le tableau , il récupère les valeurs de chaque colonne pour les utiliser dans le graphique
            valeurs = tableau.item(item, "values")

            try:
                temps = float(valeurs[4])       
                tension = float(valeurs[1])   
                intensite = float(valeurs [2])
                impedance = float(valeurs[3])
                self.x.append(temps)
                self.y.append(tension)
                self.yi.append(intensite)
                self.yimp.append(impedance)

            except ValueError:
                pass

        # Tracé du graphique
        ax.plot(self.x, self.y, marker=".", label="Tension")
        ax.plot(self.x, self.yi, marker=".", label="Intensité")
        ax.plot(self.x, self.yimp, marker=".", label="Inductance")
        ax.set_title("Courbe  / Temps")
        ax.set_xlabel("Temps [s]")
        ax.set_ylabel("Tension/Intensité/Inductance")
        ax.grid(True)
        ax.legend()

        # Rafraîchir l'affichage
        graph.draw()

# ============================================================
# LIMITE DES ENTREES
# ============================================================
frame_gauche = ttk.Frame(IHM)
frame_gauche.grid(row=0, column=0, sticky="n", padx=10, pady=10)
frame_gauche.columnconfigure(0, weight=1)

partie_parametre = ttk.LabelFrame(frame_gauche, text="Paramètre des mesures")
partie_parametre.grid(row=1, column=0, sticky="ew", pady=5)
partie_parametre.columnconfigure(0, weight=1)
class CGestion_Limite :
    ## @class CGestion_Limite
    # Classe pour la gestion des limites des entry
    def valider_Ech(new_value):
        ## @var valider_Ech
        # Verification des valeurs entrées dans les paramètres de mesures . Bloque en cas de valeurs superieur a 2000
        if new_value == "":
            return True
        try:
            val = int(new_value)
            return 1 <= val <= 2000
        except ValueError:
            return False


    validationech = (IHM.register(valider_Ech), "%P") 
    Nb_Ech = ttk.Entry(partie_parametre, validate="key", validatecommand=validationech)
    Nb_Ech.grid(row=0, column=1, sticky="ew", padx=5, pady=2)


    def valider_Feq(new_value):
        ## @var valider_Feq
        # Verification des valeurs entrées dans les paramètres de mesures . Bloque en cas de valeurs superieur a 1000
        if new_value == "":
            return True
        try:
            val = int(new_value)
            return 1 <= val <= 1000
        except ValueError:
            return False


    validationFeq = (IHM.register(valider_Feq), "%P") 
    Feq = ttk.Entry(partie_parametre, validate="key", validatecommand=validationFeq)
    Feq.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

# ------------------------------------------------------------
# INITIALISATION DU MENU 
# ------------------------------------------------------------

## @class CGestion_Interface
#@brief Classe permettant de regrouper toute l'interface de l'IHM que ce soit les boutons , les labels ou les entry

menu = tk.Menu(IHM)
gestion_csv = CGestion_Fichier_CSV()
gestion_fonction = CGestion_Fonction()
gestion_bdd=CGestion_BDD()
detection_esp32=CGestion_Connexion()
## @var menu
#@brief  Création d'un menu pour acceder au paramètre 
menu_fichier = tk.Menu(menu, tearoff=0)
menu_fichier.add_command(label="Ouvrir", command=gestion_csv.charger_csv)
menu_fichier.add_command(label="Sauvegarder", command=gestion_csv.sauvegarder_csv)
menu.add_cascade(label="Fichier", menu=menu_fichier)

menu_parametre = tk.Menu(menu, tearoff=0)
menu_parametre.add_command(label="Quitter", command=gestion_fonction.quitter)
menu.add_cascade(label="Paramètre", menu=menu_parametre)
                                            
menu_info = tk.Menu(menu, tearoff=0)
menu_info.add_command(label="Information",command=gestion_fonction.information)
menu.add_cascade(label="À propos", menu=menu_info)

IHM.config(menu=menu)


# ============================================================
# CONFIGURATION DU LAYOUT PRINCIPAL
# ============================================================
# Deux grandes colonnes
IHM.columnconfigure(0, weight=0)  # Partie gauche : Mesure + Paramètre
IHM.columnconfigure(1, weight=1)  # Partie droite : Résultat
IHM.rowconfigure(0, weight=1)


# ============================================================
# PARTIE GAUCHE : MESURE + PARAMÈTRE
# ============================================================

# ---- Zone Mesure ----
partie_mesure = ttk.LabelFrame(frame_gauche, text="Mesure")
partie_mesure.grid(row=0, column=0, sticky="ew", pady=5)
partie_mesure.columnconfigure(0, weight=1)

bouton_connexion = ttk.Button(
    partie_mesure,
    text="🔌 Connexion",
    command=detection_esp32.detecter_esp32
)
bouton_connexion.grid(row=0, column=0, pady=5, sticky="ew")

bouton_envoie = ttk.Button(
    partie_mesure,
    text="📤 Envoyer les parametres",
    command=detection_esp32.envoie_parametre
)
bouton_envoie.grid(row=1, column=0, pady=5, sticky="ew")

bouton_demarrer = ttk.Button(
    partie_mesure,
    text="▶ Démarrer",
    command=detection_esp32.demarrer_mesure
)
bouton_demarrer.grid(row=2, column=0, pady=5, sticky="ew")

bouton_reinitialiser = ttk.Button(
    partie_mesure,
    text="🔁 Reinitialiser",
    command=detection_esp32.reinitialiser
)
bouton_reinitialiser.grid(row=3, column=0, pady=5, sticky="ew")

ttk.Label(partie_mesure, text="Statuts").grid(row=4, column=0, sticky="w")
texte_status = tk.Text(partie_mesure, width=30, height=8)
texte_status.grid(row=5, column=0, pady=5)
texte_status.config(state="disabled")

# ============================================================
# ZONE PARAMETRE
# ============================================================

# ---- Zone Echantillons ----
ttk.Label(partie_parametre, text="Nombre Echantillons").grid(row=0, column=0, sticky="w", padx=5, pady=2)
partie_parametre.columnconfigure(1, weight=1)

# ---- Zone Fréquence ----
ttk.Label(partie_parametre, text="Fréquence Echantillonage").grid(row=1, column=0, sticky="w", padx=5, pady=2)
partie_parametre.columnconfigure(1, weight=1)

# ---- Zone Autre ----
partie_autre = ttk.LabelFrame(frame_gauche, text="Autre")
partie_autre.grid(row=3, column=0, sticky="ew", pady=5)
partie_autre.columnconfigure(0, weight=1)

# ---- Bouton Historique ----
bouton_historique = ttk.Button(
    partie_autre,
    text="Historique",
    command=gestion_fonction.historique
)
bouton_historique.grid(row=3, column=0, pady=5, sticky="ew")
# ---- Bouton BDD ----
bouton_BDD = ttk.Button(
    partie_autre,
    text="Base de Donnée",
    command=gestion_bdd.creer_BDD
)
bouton_BDD.grid(row=4, column=0, pady=5, sticky="ew")
# ---- Bouton Ajout-Donnée ----
bouton_AjD = ttk.Button(
    partie_autre,
    text="Ajouter Données",
    command=gestion_bdd.ajout_BDD
)
bouton_AjD.grid(row=5, column=0, pady=5, sticky="ew")


# ============================================================
# PARTIE DROITE : RÉSULTAT (TABLE + GRAPHIQUE)
# ============================================================
partie_resultat = ttk.LabelFrame(IHM, text="Résultat")
partie_resultat.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
partie_resultat.columnconfigure(0, weight=1)
partie_resultat.rowconfigure(0, weight=1)
partie_resultat.rowconfigure(1, weight=1)

# ----- Graphique -----
fig, ax = plt.subplots(figsize=(6, 4))
graph = FigureCanvasTkAgg(fig, master=partie_resultat)
graph.get_tk_widget().grid(row=0, column=0, sticky="nsew", pady=5)

# ----- Table -----
tableau = ttk.Treeview(partie_resultat, columns=("E","Tens","Int","I","T"), show="headings", height=8 )
tableau.heading("E", text="Echantillon")
tableau.heading("I", text="Inductance")
tableau.heading("T", text="Temps [s]")
tableau.heading("Tens", text="Tension [v]")
tableau.heading("Int", text="Intensité [A]")
tableau.grid(row=1, column=0, sticky="nsew")
# ---- Menu Déroulant ----
menu_deroulant= ttk.Scrollbar(partie_resultat,orient="vertical",command=tableau.yview)
tableau.configure(yscrollcommand=menu_deroulant.set)
menu_deroulant.grid(row=1 , column=1 , sticky="ns")

# ============================================================
# LANCEMENT DE L'IHM
# ============================================================
IHM.mainloop()
 

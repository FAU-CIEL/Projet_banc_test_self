"""
@file IHM_BancTest.py
@brief Simulateur graphique de banc de test électrique
@author Leroux Erwan
@version 1.0
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import sqlite3

IHM=tk.Tk()
IHM.title("Simulateur Banc de Test")
IHM.geometry("1200x700")


menu=tk.Menu(IHM)
menu_fichier=tk.Menu(menu,tearoff=0)
menu.add_cascade(label="Fichier",menu=menu_fichier)
menu_fichier.add_command(label="Open")
menu_fichier.add_command(label="Sauvegarder")
menu_option = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Parametre",menu=menu_option)
menu_option.add_command(label="Quitter")
Info= tk.Menu(menu, tearoff=0)
menu.add_cascade(label="A Propos",menu=Info)
Info.add_command(label="Information")
IHM.config(menu=menu)

"""
@Initialisation de l'IHM
"""
IHM.mainloop()
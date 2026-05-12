#import numpy as np
import matplotlib.pyplot as plt
from time import time, sleep
import select
import sys
import numpy as np
import array


import classe as cl

"""
bibliotheque/fonction en commentaire pour la compilation en microPython
"""

# ==============================
# Fonctions utiles
# ==============================


def affichage(x, y, title=None, label=None, color=None, xlabel=None, ylabel=None):
    plt.figure()
    plt.plot(x, y, color=color, label=label)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid()


def attendre_terminal(timeout=None):
    start = time()
    while True:
        if select.select([sys.stdin], [], [], 0)[0]:
            break
        
        if timeout is not None and (time() - start) > timeout:
            break
        
        sleep(0.1)
    

    


# ==============================
# Parametres du banc de test
# ==============================
def main():

    #attendre_terminal()

    banc_test = cl.Simulation()

    banc_test.initialisation(
        Vm=500.0,       # Tension de mesure (V)
        I_max=20.0,    # Courant max visé (A)   # inutile actuellement
        R_self=0.1,    # Resistance ohmique de la self (Ω)

        L0=5e-3,       # Inductance a faible courant (H)
        I_sat=15.0,    # Courant de saturation (A)

        fs=2e6,        # fréquence d'échantillonnage ( 2MS/s )
        C_bus=10e-3    # Capaciter du banc de condensateur (F)
    )

    # ==============================
    # simulation de l'impulsion
    # ==============================

    t, i, u, V_c = banc_test.run()

    # ==============================
    # calcul des grrandeurs magnetiques
    # ==============================

    # inductance incrementale
    L_inc = banc_test.inductance_non_lineaire(i) - banc_test.inductance_non_lineaire(0)

    # inductance secante
    L_sec = banc_test.inductance_non_lineaire(i)

    # flux magnetique ψ(i) = ∫u dt
    psi = np.cumsum(u) * banc_test.dt

    # ==============================
    # Affichage des resultats
    # ==============================

    
    affichage(i, L_sec, title="Inductance secante", label="Inductance secante Lsec(i)", color='lime', xlabel='Courant (A)', ylabel="Lsec (H)")
    affichage(i, L_inc, title="Inductance incrementale", label="Linc(i)", color='green', xlabel='Courant (A)', ylabel="Linc (H)")
    affichage(i, psi, title="Flux magnétique", label="ψ(i)", color='black', xlabel='Courant (A)', ylabel="Flux ψ (Wb)")
    affichage(list(map( lambda x: x * 1e3, t)), i, title="Courant Bobine i(t)", label='Courant bobine i(t)', color='blue', xlabel='Temps (ms)', ylabel='Courant (A)')
    affichage(list(map( lambda x: x * 1e3, t)), V_c, title="Tension Condensateur Vc(t)", label='Tension condensateur Vc(t)', color='orange', xlabel='Temps (ms)', ylabel='Tension (V)')

    plt.figure()
    plt.plot(list(map( lambda x: x * 1e3, t)), i, label='Courant bobine i(t)')
    plt.plot(list(map( lambda x: x * 1e3, t)), V_c, label='Tension condensateur Vc(t)')
    plt.xlabel('Temps (ms)')
    #plt.ylabel('i(t) / Vc(t)')
    plt.title("Courant Bobine et Tension Condensateur")
    plt.legend()
    plt.grid()
    

    # ==============================
    # Tableau des resultats
    # ==============================
    
    print("Temps (ms) | Courant Bobine (A) | Tension Condensateur (V)")
    print("----------------------------------------------------------")
    for k in range(len(t)):
        print(f"{t[k]*1e6:9.2f} | {i[k]:18.6f} | {V_c[k]:23.6f}")
    
    
    plt.show()
    
if __name__ == "__main__":
    main()


# verifier diff numpy.ndarray et list
# supprimer numpy
# verifer fonction avec array
# changer boucle for en remplacant le temps par la decharge du condo

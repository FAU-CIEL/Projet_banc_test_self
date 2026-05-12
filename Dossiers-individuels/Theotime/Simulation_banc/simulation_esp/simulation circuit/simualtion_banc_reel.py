# Simulation numérique d’un banc de test de self (inductance)
# Basé sur le principe de mesure impulsionnelle (pulse measurement)
# Références principales :
# - ed-k / Power Choke Tester DPG10/20 (Hubert Kreis, 2021)
# - Relations physiques fondamentales : u = L(i) * di/dt
# Objectif : reproduire i(t), u(t), Linc(i), Lsec(i), flux ψ(i)

import numpy as np
import matplotlib.pyplot as plt

import classe as cl

# ==============================
# Fonctions utiles
# ==============================

def affichage(x, y, title=None, label=None, color=None, xlabel=None, ylabel=None):
    # Affiche des resultats
    plt.figure()
    plt.plot(x, y, color=color, label=label)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid()
    

# ==============================
# Parametres du banc de test
# ==============================

Vm = 50.0 # Tension de mesure (V)
I_max = 20.0 # Courant max visé (A)
R_self = 0.1 # Resistance ohmique de la self (Ω)

# Parametre du noyau (modele simplifié)
L0 = 5e-3 # Inductance a faible courant (H)
I_sat = 15.0 # Courant de saturation (A)

# Parametre temporel
fs = 2e6 # fréquence d'échantillonnage ( 2MS/s )
dt = 1 / fs

# ==============================
# Modele d'inductance non linéaire L(i)
# ==============================

def inductance_non_lineaire(i):
    """ 
    Modele simple de saturation magnetique
    L(i) = L0 / (1 + (i/I_sat)^2)
    """
    return L0 / (1 + (i / I_sat) ** 2)

# ==============================
# Parametres du condensateur d'allimentation
# ==============================

C_bus = 10e-3   # Capaciter du banc de condensateur (F)
V_c = [Vm]      # Tension initiale du condensateur (V)


# ==============================
# simulation de l'impulsion
# ==============================

t = [0.0]
i = [0.0]
u = []

# Simulation sur une duree fixe
T_sim = 5e-3
N_step = int(T_sim / dt)

#while i[-1] < I_max and V_c[-1] > 0 and len(t) < N_sim:
for _ in range(N_step):
    if V_c[_] < 0:
        V_c[_] = 0.0 # Decharge du condensateur, tension ne peut pas devenir negative
    L = inductance_non_lineaire(i[-1])
    di_dt = (Vm - R_self * i[-1]) / L
    i_next = i[-1] + di_dt * dt

    t.append(t[-1] + dt)
    i.append(i_next)

    # decharge du condensateur : i = -C * dv/dt
    dV_dt = -i[-1] / C_bus
    V_c.append(V_c[-1] + dV_dt * dt)
    u.append(Vm)

# Conversion en numpy

t = np.array(t[:-1])
i = np.array(i[:-1])
u = np.array(u)
V_c = np.array(V_c[:-1])

# ==============================
# Calcul des grandeurs magnetiques
# ==============================

# Inductance incrementale
L_inc = np.gradient(i, t)
L_inc = u / L_inc

# inductance secante
L_sec = np.zeros_like(i)
L_sec[1:] = np.trapezoid(u[:len(t)], t) / i[1:]


# flux ψ(i) = ∫u dt
psi = np.cumsum(u) * dt

# ==============================
# Affichage des resultats
# ==============================


affichage(i, L_sec, title="Inductance secante", label="Inductance secante Lsec(i)", color='lime', xlabel='Courant (A)', ylabel="Lsec (H)")
affichage(i, L_inc, title="Inductance incrementale", label="Linc(i)", color='green', xlabel='Courant (A)', ylabel="Linc (H)")
affichage(i, psi, title="Flux magnétique", label="ψ(i)", color='black', xlabel='Courant (A)', ylabel="Flux ψ (Wb)")
affichage(t * 1e3, i, title="Courant Bobine i(t)", label='Courant bobine i(t)', color='blue', xlabel='Temps (ms)', ylabel='Courant (A)')
affichage(t * 1e3, V_c, title="Tension Condensateur Vc(t)", label='Tension condensateur Vc(t)', color='orange', xlabel='Temps (ms)', ylabel='Tension (V)')


plt.figure()
plt.plot(t * 1e3, i, label='Courant bobine i(t)')
plt.plot(t * 1e3, V_c, label='Tension condensateur Vc(t)')
plt.xlabel('Temps (ms)')
#plt.ylabel('i(t) / Vc(t)')
plt.title("Courant Bobine et Tension Condensateur")
plt.legend()
plt.grid()


# =============================
# Tableau des resultats
# =============================

print("Temps (µs) | Courant Bobine (A) | Tension Condensateur (V)")
print("---------------------------------------------------------")
for k in range(len(t)):
    print(f"{t[k]*1e6:9.2f} | {i[k]:18.6f} | {V_c[k]:23.6f}")


plt.show()
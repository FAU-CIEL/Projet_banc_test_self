import numpy as np
import matplotlib.pyplot as plt

# Fonction pour calculer le courant i(t) dans un circuit RL avec tension constante V
# Équation : i(t) = (V/R) * (1 - exp(-R*t/L)) + i0 * exp(-R*t/L)
def courant_RL(t, V, R, L, i0):
    return (V / R) * (1 - np.exp(-R * t / L)) + i0 * np.exp(-R * t / L)

# Demander les paramètres d'entrée : voltage V et intensité initiale i0
# Note : Pour la simulation complète, on a besoin de R et L aussi. Je les fixe ici à des valeurs par défaut,
# mais tu peux les modifier ou les demander en entrée si tu veux.
V = float(input("Entrez la tension V (en volts) : "))
i0 = float(input("Entrez l'intensité initiale i0 (en ampères) : "))

# Paramètres fixes (tu peux les changer ou les demander)
R = 10  # Résistance en ohms
L = 0.1  # Inductance en henrys

# Générer le temps t de 0 à 5 * (L/R) pour voir la réponse transitoire
t_max = 5 * (L / R)
t = np.linspace(0, t_max, 1000)

# Calculer le courant i(t)
i = courant_RL(t, V, R, L, i0)

# Afficher la valeur de l'inductance L (constante)
print(f"L'inductance de la bobine est L = {L} henrys")

# Tracer la courbe du courant i(t)
plt.figure(figsize=(10, 6))
plt.plot(t, i, label=f'Courant i(t) avec V={V}V, R={R}Ω, L={L}H, i0={i0}A')
plt.title('Simulation d\'un circuit RL : Courbe du courant')
plt.xlabel('Temps t (secondes)')
plt.ylabel('Courant i (ampères)')
plt.grid(True)
plt.legend()
plt.show()

# Afficher quelques valeurs du courant à des instants spécifiques
print("\nQuelques valeurs du courant i(t) :")
for ti in [0, t_max/4, t_max/2, 3*t_max/4, t_max]:
    idx = np.argmin(np.abs(t - ti))
    print(f"À t = {ti:.3f} s, i = {i[idx]:.3f} A")
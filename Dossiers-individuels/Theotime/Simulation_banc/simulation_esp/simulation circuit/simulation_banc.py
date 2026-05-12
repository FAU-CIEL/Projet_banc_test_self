import math
import matplotlib.pyplot as plt
import numpy as np

# Paramètres du circuit
Charge_condensateur = 0.2  # Farads
Inductance_bobine = 0.1  # Henrys

C1 = 1.0  # Constante pour la première composante
C2 = 1.0  # Constante pour la deuxième composante
Te = 0.02  # Période d'échantillonnage en secondes


def f(t):
    return C1 * np.exp((1 / math.sqrt(Inductance_bobine * Charge_condensateur)) * t) + C2 * np.exp(-(1 / math.sqrt(Inductance_bobine * Charge_condensateur)) * t)

def f2(z):
    return (C1 * z)/(z - np.exp(Te / (math.sqrt(Inductance_bobine * Charge_condensateur)))) + (C2 * z)/(z - np.exp(-Te / (math.sqrt(Inductance_bobine * Charge_condensateur))))

# Simulation de la réponse du circuit RLC
t = np.linspace(0, 1, 100)
y = f(t)

n = np.arange(0, 1, Te)
x = f2(n)


plt.plot(t, y)
plt.plot(n, x)
plt.title("Simulation de la réponse du circuit RLC")
plt.xlabel("Temps (s)")
plt.ylabel("signal en fonction du temps")
plt.grid(True)
plt.show()
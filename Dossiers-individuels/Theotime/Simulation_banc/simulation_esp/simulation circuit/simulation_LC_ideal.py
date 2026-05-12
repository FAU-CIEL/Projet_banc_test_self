import matplotlib.pyplot as plt
import math

#  ==============================
#  Parametres physiques
#  ==============================
L = 0.3  # Inductance (H) 10e-3
C = 0.2  # Capaciter (F) 100e-6
Te = 0.01  # Periode d'echantillonnage (s) 1e-5

# pulsation propre
omega_0 = 1 / (L * C) ** 0.5

# ==============================
# Condition initiale
# ==============================

U0 = 50 # Tension initiale du condensateur (V)

# i(0) = 0
i_nm2 = 0.0     # i[n-2]
i_nm1 = U0 * (C / L) ** 0.5 * math.sin(omega_0 * Te)     # i[n-1]

# ==============================
# Parametre numerique
# ==============================

alpha = 2 - (Te ** 2) / (L * C)


# ==============================
# Stockage des resultats
# ==============================

iL_list = []  # Courant dans la bobine
uL_list = []  # Tension aux bornes de la bobine
time = []

# ==============================
# Boucle de simulation
# ==============================

N = 1000 # Nombre d'iterations

for n in range(N):
    
    # -- calcul du courant (equation diff) --
    i_n = alpha * i_nm1 - i_nm2

    # -- calcul de la tension aux bornes de la bobine --
    u_L = (L / Te) * (i_n - i_nm1)

    # -- sauvegarde --
    iL_list.append(i_n)
    uL_list.append(u_L)
    time.append(n * Te)

    # -- decalage des etats --
    i_nm2 = i_nm1
    i_nm1 = i_n


# ==============================
# Affichage des resultats
# ==============================

print("temps : ", time)
print("courant dans la bobine : ", iL_list)
print("tension aux bornes de la bobine : ", uL_list)


plt.figure(figsize=(10, 6))
#plt.subplot(2, 1, 1)
plt.title('Simulation du circuit LC ideal')
plt.plot(time, iL_list, label='Courant dans la bobine (A)')
plt.xlabel('Temps (s)')
plt.ylabel('Courant (A)')
#plt.grid()

#plt.subplot(2, 1, 2)
plt.plot(time, uL_list, label='Tension aux bornes de la bobine(V)', color='orange')
plt.xlabel('Temps (s)')
plt.ylabel('Tension (V)')
plt.grid()
plt.tight_layout()
plt.show()


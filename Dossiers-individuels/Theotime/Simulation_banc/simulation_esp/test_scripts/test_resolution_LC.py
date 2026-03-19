import matplotlib.pyplot as plt

# ====================
# Paramètres circuit
# ====================

L = 0.5         # Inductance en Henry
C = 0.001       # Capacité en Farads
q0 = 1.0        # Charge initiale en Coulombs
i0 = 0.0        # Courant initiale en Ampères

# ====================
# Paramètres simulation
# ====================

dt = 0.0001     # Pas de temps en seconde
steps = 10000    # Nombres d'itérations

# ====================
# fonctions
# ====================

def deriv(q, i, L, C):
    """
    Calcule les dérivées dq/dt et di/dt pour le circuit LC.
    """
    dq_dt = i
    di_dt = -(1 / (L * C)) *q
    return dq_dt, di_dt

def euler_step(q, i, L, C, dt):
    """
    Effectue un pas de la méthode d'Euler.
    """
    dq_dt, di_dt = deriv(q, i, L, C)
    q_new = q + dq_dt * dt
    i_new = i + di_dt * dt
    return q_new, i_new

def simulate_lc(L, C, q_init, i_init, dt, steps):
    """
    Simule le circuit LC et affiche les resultats.
    """

    temps = []
    charge = []
    courant = []
    q = q_init
    i = i_init

    for step in range(steps):
        t = step * dt
        q, i = euler_step(q, i, L, C, dt)
        
        temps.append(t)
        charge.append(q)
        courant.append(i)
    
    return temps, charge, courant

temps, charge, courant = simulate_lc(L, C, q0, i0, dt, steps)

print("t(s)\tq(C)\ti(A)")
for i in range(len(temps)):
    print("{:.6f}\t{:.6f}\t{:.6f}".format(temps[i], charge[i], courant[i]))

plt.figure()
plt.plot(temps, charge, label='Charge (C)')
plt.plot(temps, courant, label='Courant (A)')
plt.title('Simulation d\'un circuit LC')
plt.xlabel('Temps (s)')
plt.ylabel('Charge (C) / Courant (A)')
plt.legend()
plt.grid()
plt.show()
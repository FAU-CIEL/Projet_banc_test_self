import matplotlib.pyplot as plt
import numpy as np

def affichage(x, y, title=None, label=None, color=None, xlabel=None, ylabel=None):
    # Affiche des resultats
    plt.figure()
    plt.plot(x, y, color=color, label=label)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid()


class Simulation:
    def __init__(self):
        self.Vm = 0
        self.I_max = 0
        self.R_self = 0

        self.L0 = 0
        self.I_sat = 0

        self.fs = 0
        self.dt = 0

        self.C_bus = 0

    
    def initialisation(self, Vm, I_max, R_self, L0, I_sat, fs, C_bus):
        self.Vm = Vm
        self.I_max = I_max
        self.R_self = R_self

        self.L0 = L0
        self.I_sat = I_sat

        self.fs = fs
        self.dt = 1 / fs

        self.C_bus = C_bus

    def inductance_non_lineaire(self, i):

        # modele simple de saturation magnetique : L(i) = L0 / (1 + (i/I_sat)^2)
        return self.L0 / (1 + (i / self.I_sat) ** 2)
    
    def run(self):
        # Initialisation des listes de resultats
        t = [0.0]
        i = [0.0]
        V_c = [self.Vm]  # Tension initiale du condensateur
        u = []
        
        # Simulation sur une duree fixe
        T_sim = 5e-3
        N_step = int(T_sim / self.dt)
        for _ in range(N_step):
            if V_c[_] < 0:
                V_c[_] = 0.0 # Decharge du condensateur, tension ne peut pas devenir negative
            L = self.inductance_non_lineaire(i[-1])
            di_dt = (self.Vm - self.R_self * i[-1]) / L
            i_next = i[-1] + di_dt * self.dt

            t.append(t[-1] + self.dt)
            i.append(i_next)

            # decharge du condensateur : i = -C * dv/dt
            dV_dt = -i[-1] / self.C_bus
            V_c.append(V_c[-1] + dV_dt * self.dt)
            u.append(self.Vm)

        # Conversion en numpy
        t = np.array(t[:-1])
        i = np.array(i[:-1])
        u = np.array(u)
        V_c = np.array(V_c[:-1])

        return t, i, u, V_c


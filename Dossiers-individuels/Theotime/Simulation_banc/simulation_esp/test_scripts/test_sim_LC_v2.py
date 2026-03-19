import math
import matplotlib.pyplot as plt

class Simulation:
    def __init__(self, C, L, U0=1.0, I0=0.0, dt=1e-4, duree=0.01):
        """
        C : capacité (F)
        L : inductance (H)
        U0: tension initiale du condensateur (V)
        I0: courant initial (A)
        dt : pas de temps (s)
        duree : durée totale de simulation (s)
        """
        self.C = float(C)
        self.L = float(L)
        self.U0 = float(U0)
        self.I0 = float(I0)
        self.dt = float(dt)
        self.duree = float(duree)

        # constante propre
        self.omega0 = 1.0 / math.sqrt(self.L * self.C)

        # nombre pas
        self.n_steps = int(max(1, math.ceil(self.duree / self.dt)))

    def calcul_equation_diff(self):
        """
        Retourne des informations analytiques sur l'ODE et des fonctions analytiques
        utilisables pour vérification :
        - omega0
        - fonction u_analytique(t)
        - fonction i_analytique(t)
        """
        def u_analytique(t):
            return self.U0 * math.cos(self.omega0 * t) + (self.I0 / (self.C * self.omega0)) * math.sin(self.omega0 * t)
        
        def i_analytique(t):
            return self.I0 * math.cos(self.omega0 * t) - self.C * self.U0 * self.omega0 * math.sin(self.omega0 * t)
        
        return {
            'omega0': self.omega0,
            'u_analytique': u_analytique,
            'i_analytique': i_analytique
        }
    
    def transformee_Z(self):
        """
        Retourne les coefficients de l'équation en différences:
        u_{n+1} - (2 - alpha)*u_n + u_{n-1} = 0
        avec alpha = omega0^2 * dt^2
        On retourne aussi le polynôme caractéristique en z: z^2 - (2 - alpha) z + 1
        """
        alpha = (self.omega0 ** 2) * (self.dt ** 2)
        a_plus = 1.0                                # coefficient of u_{n+1}
        a_zero = -(2.0 - alpha)                     # coefficient of u_n (moved to left)
        a_minus = 1.0                               # coefficient of u_{n-1}
        poly_descr = "z^2 - (2 - alpha) z + 1 where alpha = omega0^2 * dt^2 = {:.6g}".format(alpha)
        return {
            'alpha': alpha,
            'coefficients': (a_plus, a_zero, a_minus),
            'char_poly_z': poly_descr
        }
    
    def decharge_condentateur(self):
        """
        Simule la décharge du condensateur : lance la simulation avec les conditions
        initiales fournies (U0, I0).
        Retourne t_list, i_list, u_list
        """
        return self.simulation()
    
    def simulation(self):
        """
        Méthode principale : calcule et renvoie trois listes (t, i, u)
        - t : instants (float)
        - u : tension aux bornes du condensateur (V)
        - i : courant dans la bobine (A)
        Schéma: différences finies centrées pour u, courant par différence backward.
        """
        # stability check (simple)
        stability_ok = (self.omega0 * self.dt) <= 2.0

        # allocate lists
        t_list = [0.0] * (self.n_steps + 1)
        u_list = [0.0] * (self.n_steps + 1)
        i_list = [0.0] * (self.n_steps + 1)

        # initial conditions: u(0) = U0, i(0) = I0
        u_list[0] = self.U0
        i_list[0] = self.I0
        t_list[0] = 0.0

        # To start recurrence we need u_{-1}. Use backward difference consistent with i(0):
        # i(0) = C*(u(0) - u(-1))/dt  =>  u(-1) = u(0) - i(0)*dt/C
        u_minus1 = u_list[0] - i_list[0] * self.dt / self.C

        # compute first step u1 by using recurrence rearranged for u1:
        # u1 = (2 - omega0^2 dt^2) * u0 - u_{-1}
        alpha = (self.omega0 ** 2) * (self.dt ** 2)
        u1 = (2.0 - alpha) * u_list[0] - u_minus1
        if self.n_steps >= 1:
            u_list[1] = u1
            t_list[1] = self.dt
            # compute i(1) by backward difference i(1) = C*(u1 - u0)/dt
            i_list[1] = self.C * (u1 - u_list[0]) / self.dt

        # time stepping
        for n in range(1, self.n_steps):
            t_n = n * self.dt
            t_list[n] = t_n
            # recurrence: u_{n+1} = (2 - alpha) u_n - u_{n-1}
            u_np1 = (2.0 - alpha) * u_list[n] - u_list[n-1]
            u_list[n+1] =u_np1
            # current (backward difference)
            i_list[n+1] = self.C * (u_list[n+1] - u_list[n]) / self.dt

        # fill last time value (in case of rounding)
        t_list[self.n_steps] = self.n_steps * self.dt
        info = {
            'stability_ok': stability_ok,
            'omega0_dt': self.omega0 * self.dt,
            'alpha': alpha
        }
        return t_list, i_list, u_list, info
    
if __name__ == "__main__":
    sim = Simulation(C=1e-6, L=1e-3, U0=5.0, I0=0.0, dt=1e-6, duree=0.002)
    t, i, u, info = sim.simulation()
    print(print("stability_ok:", info['stability_ok'], "omega0*dt=", info['omega0_dt']))
    # afficher quelques valeurs
    for k in range(len(t)):
        print(k, t[k], "U=", u[k], "I=", i[k])

    # tracer les résultats numériques et les comparer à la solution analytique
    analyt = sim.calcul_equation_diff()
    u_ana = [analyt['u_analytique'](tt) for tt in t]
    i_ana = [analyt['i_analytique'](tt) for tt in t]

    fig, ax_u = plt.subplots()
    ax_u.plot(t, u, label="u simulation", color="C0")
    ax_u.plot(t, u_ana, "--", label="u analytique", color="C0", alpha=0.6)
    ax_u.set_xlabel("t (s)")
    ax_u.set_ylabel("u (V)")
    ax_u.legend(loc="upper right")

    ax_i = ax_u.twinx()
    ax_i.plot(t, i, label="i simulation", color="C1")
    ax_i.plot(t, i_ana, "--", label="i analytique", color="C1", alpha=0.6)
    ax_i.set_ylabel("i (A)")
    ax_i.legend(loc="lower right")

    plt.title("Simulation LC : mesures (points) et solution analytique (trait)")
    plt.grid(True)
    plt.show()
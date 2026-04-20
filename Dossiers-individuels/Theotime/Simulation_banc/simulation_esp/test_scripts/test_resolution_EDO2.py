
def resolution_EDO2(f, t0, y0, dy0, h, n):
    """
    f: fonction f(t, y, dy) representant y'' = f(...)
    t0: temps initial
    y0: valeur initiale de y
    dy0: valeur initiale de y'
    h: pas de temps
    n: nombre d'iterations
    """

    t = t0
    y = y0
    dy = dy0

    # stokage des resultats
    T = [t]
    Y = [y]

    for _ in range(n):
        # clacul de y'' a partir de f
        ddy = f(t, y, dy)

        # mise a jour par Euler
        y_new = y + h * dy
        dy_new = dy + h * ddy

        # avance dans le temps
        t += h
        y, dy = y_new, dy_new

        # sauvegarde
        T.append(t)
        Y.append(y)

    return T, Y

# definition de l'équation : y'' = -2y' -5y
def f(t, y, dy):
    return -2 * dy - 5 * y

def main():
    # parametres
    t0 = 0.0
    y0 = 1.0
    dy0 = 0.0
    h = 0.01 # pas de temps
    n = 1000 # nombre d'iterations

    # resolution
    T, Y = resolution_EDO2(f, t0, y0, dy0, h, n)

    # affichage simple

    for i in range(0, len(T), 100):
        print("t = {:.2f}, y = {:.4f}".format(T[i], Y[i]))


"""
import matplotlib.pyplot as plt

plt.plot(T, Y, label='y(t)')
plt.title("Résolution de l'EDO y'' = -2y' -5y")
plt.xlabel('Temps (s)')
plt.ylabel('y(t)')
plt.grid()
plt.legend()
plt.show()
"""
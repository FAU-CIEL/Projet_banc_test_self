import matplotlib.pyplot as plt
import json

INPUT_FILE = "D:/fauret.SNIRW/Projet_banc_test_self/Dossiers-individuels/Theotime/Simulation_banc/simulation_esp/LOG/data_recu.json"


if __name__ == "__main__":
    with open(INPUT_FILE, 'r') as file:
        valeur_json = json.load(file)
    file.close()

    valeur_temps = valeur_json["temps"]
    valeur_tension = valeur_json["tension"]
    valeur_intensiter = valeur_json["intensite"]

    plt.figure()
    plt.plot(valeur_temps, valeur_tension, color='blue', label="u(t)")
    #plt.stem(valeur_temps, valeur_tension, label="u(t)")
    plt.title("u(t)")
    plt.xlabel("temps")
    plt.ylabel("tension")
    plt.legend()
    plt.grid()

    plt.figure()
    plt.plot(valeur_temps, valeur_intensiter, color='orange', label="i(t)")
    #plt.stem(valeur_temps, valeur_intensiter, label="i(t)")
    plt.title("i(t)")
    plt.xlabel("temps")
    plt.ylabel("intensiter")
    plt.legend()
    plt.grid()

    plt.figure()
    plt.plot(valeur_temps, valeur_tension, color='blue', label="u(t)")
    plt.plot(valeur_temps, valeur_intensiter, color='orange', label="i(t)")
    plt.title("u(t) et i(t)")
    plt.xlabel("temps")
    plt.ylabel("tension / intensiter")
    plt.grid()

    plt.show()

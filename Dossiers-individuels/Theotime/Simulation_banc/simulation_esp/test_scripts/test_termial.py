import sys
import time
import select


def essayer_terminal(timeout=None):
    """
    Attend qu'une entrée soit détectée sur le terminal série.
    timeout : en secondes (None = infini)
    """
    print("En attente d'un terminal...")
    start = time.time()
    while True:
        # Vérifie si les données arrivent depuis le terminal
        if select.select([sys.stdin], [], [], 0)[0]:
            print("Terminal detecte, execution du script...")
            break

        # Vérifie le timeout
        if timeout is not None and (time.time() - start) > timeout:
            print("Timeout atteint, aucun terminal detecte.")
            break
        
        time.sleep(0.1)

def main1():
    essayer_terminal(timeout=5)
    essayer_terminal()
    print("Script principal execute.")
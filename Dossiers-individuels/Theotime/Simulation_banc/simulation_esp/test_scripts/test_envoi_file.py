import sys

FILENAME = "envoi_esp.json"

try:
    sys.stdout.write("__START__\n")
    with open(FILENAME, "r") as f:
        for line in f:
            sys.stdout.write(line.strip() + "\n")
    sys.stdout.write("__END__\n")
except OSError:
    sys.stdout.write("ERREUR: Fichier introuvable\n")
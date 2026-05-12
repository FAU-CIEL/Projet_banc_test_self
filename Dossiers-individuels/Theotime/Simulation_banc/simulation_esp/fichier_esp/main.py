import Classes   # type:ignore
import gc        # classe pour la gestion de la memoire (HEAP)

while True:
    banc_de_test_self = Classes.Gestion_fonction()
    banc_de_test_self.loop()
    del banc_de_test_self
    gc.collect()
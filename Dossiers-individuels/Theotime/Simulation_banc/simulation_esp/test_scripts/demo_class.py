class essalc2:
    def __init__(self):
        pass

    def premiere_chose(self):
        print(2)
    
    def deuxieme_chose(self):
        print("deux")

class classe1:
    def __init__(self):
        pass

    def premier_truc(self):
        print(1)
    
    def deuxieme_truc(self):
        print("un")


class gestion:
    def __init__(self):
        self.un_truc = classe1()
        self.une_chose = essalc2()

    def loop(self):
        self.un_truc.premier_truc()
        self.une_chose.premiere_chose()
        self.un_truc.deuxieme_truc()
        self.une_chose.deuxieme_chose()

quelque_chose = gestion()
quelque_chose.loop()
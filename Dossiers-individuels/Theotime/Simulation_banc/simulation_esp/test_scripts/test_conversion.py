import array

def calcul_tableau(x):
    return x/2

ma_liste1 = [1,2,3,4,5]
print("type de ma_liste1:", type(ma_liste1))
print(ma_liste1)

ma_liste2 = array.array('f', ma_liste1)
print("type de ma_liste2:", type(ma_liste2))
print(ma_liste2)
print("Element à l'index 2:", ma_liste2.__getitem__(-1))

ma_liste1_calcul = map(calcul_tableau, ma_liste1)
ma_liste2_calcul = map(calcul_tableau, ma_liste2)

print("ma_liste1_calcul:", list(ma_liste1_calcul))
print("ma_liste2_calcul:", list(ma_liste2_calcul))
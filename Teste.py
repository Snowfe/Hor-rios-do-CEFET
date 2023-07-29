import copy
lista = [1, 2, [3, 4, [5, 6]]]
lista2 = copy.deepcopy(lista)

lista[2][2][1] = 7

print(lista)
print(lista2)

lista2[2][2] = lista[2][2]
lista[2][2][0] += 1

print(lista)
print(lista2)

lista3 = [0 for c in range(0, 10)]
print(lista3)
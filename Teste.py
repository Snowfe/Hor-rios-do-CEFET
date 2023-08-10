

l1 = [1, 1, 1, 1, 1, 1, 1, 1, 1]
l2 = [2, 2, 2, 2, 2, 2]

listas_juntas = l1 + l2
print(listas_juntas)

resultado = []
c = 0
while len(listas_juntas) != 0:
    if c % 2 == 0:
        resultado.append(listas_juntas[0])
        listas_juntas = listas_juntas[1:]
    else:
        resultado.append(listas_juntas[-1])
        listas_juntas = listas_juntas[:-1]
    c += 1

print(resultado)
import copy
class T():
    def __init__(self, lista) -> None:
        self.lista = lista

x = T([1,2,3,4])
y = T([5,6,7,8])
valores = [x, y]
values = copy.deepcopy(valores)
values[0].lista.append('X')
print(x.lista, values[0].lista)
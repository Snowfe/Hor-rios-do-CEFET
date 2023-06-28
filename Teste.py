import functions.logic as l

class Exemplo:
    def __init__(self, tipo):
        self.type = tipo
x = Exemplo(tipo='3,1,G')
print(x.type)
quadro = {'MEC-2A':{
                '2': [[[0, 0, 0, 0], 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],  # manhã e tarde
                '3': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
                '4': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
                '5': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
                '6': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]]
            }}
l.replace_h(quadro, 'MEC-2A', 0, x, '2', 0, 0, '3', 4, pb_1=3, pb_2=2)
for x in quadro['MEC-2A'].values():
    print(x)


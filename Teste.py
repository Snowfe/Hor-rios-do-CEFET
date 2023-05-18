def bimestrals_organizer(lista_b):
    """
    Aqui vamos organizar os horários bimestrais
    Os horários bimestrais estão sendo colocados dentro de listas, essas listas são diferentes de acordo com o tipo do horário
    Os horários bimestrais podem ser de 3 tipos, os que tem duração de 1 bimestre, dois bimestres e de 4 bimestres

    1 bimestres  2 bimestres   3 bimestres
    [A, B, C, 0]   [A, B]        [A, B]
    [0, A, B, C]   [B, A]
    [C, 0, A, B]
    [B, C, 0, A]
     
    Os horários em sequência, devem ser organizados da mesma forma
    """
    if len(lista_b) == 4:
        result = []
        for c in range(0, 4):
            bimestre = [0, 0, 0, 0]
            for d in range(0, 4):
                v = (d + c) % 4
                bimestre[d] = lista_b[v]
            result.append(bimestre)
        return result
    
valor = bimestrals_organizer(['A', 'B', 'C', 0])
print(valor)
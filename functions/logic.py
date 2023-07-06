# Arquivo com as funções envolvendo a lógica do nosso programa

import random
from functions import loadData

"""
Regras Básicas:
- não mudar o board dentro das funções
"""


def getBetterHour(horario, board, subjectPos, typeNum):
    motivo = 0
    quadro = board.copy()
    if not('0' in horario.type):
        if '1' == horario.type[2]:
            n_bimestres = 4
        elif '4,G' in horario.type:
            n_bimestres = 3
        elif 'T' in horario.type:
            n_bimestres = 2
        else:
            print('Não corresponde a nenhum', horario, horario.type)
    betterH = [['', -999]]  # (day;hour, pontuação), melhores horários
    # Se for horário bimestral será (day;hour;bimestre, pontuação)

    teacher = horario.teacher
    turm = horario.turm
    subject = horario.subject

    for d in range(2, 7):  # para cada dia
        d = str(d)
        n_horarios = 4 if typeNum == 2 else 6
        for h in range(0, n_horarios):  # para cada horário no dia
            if teacher.bimestral[subjectPos] == 0: # Se horário não for bimestral
                pontuation, motivo = validation(horario, [d, h], quadro, subjectPos, typeNum) 
                if pontuation == 0:
                    pontuation = cost_individual(horario, [d, h], quadro, subjectPos, typeNum)
                    if pontuation > betterH[0][1]:
                        betterH = [[f'{d};{h}', pontuation]]
                    elif pontuation == betterH[0][1]:
                        betterH.append([f'{d};{h}', pontuation])

            else: # Se for
                for bimester in range(0, n_bimestres):
                    #print('BIMESTRE -->', bimester)
                    pontuation, motivo = validation(horario, [d, h, bimester], quadro, subjectPos, typeNum, bimestral=1)
                    if pontuation == -100:
                        continue # Ou break?
                    if pontuation == 0:
                        pontuation = cost_individual(horario, [d, h, bimester], quadro, subjectPos, typeNum, bimestral=1)
                        if pontuation > betterH[0][1]:
                            betterH = [[f'{d};{h};{bimester}', pontuation]]
                        elif pontuation == betterH[0][1]:
                            betterH.append([f'{d};{h};{bimester}', pontuation])
                        
                        #print(pontuation, d, h, bimester)
    result = random.choice(betterH)[0]
    #result = betterH[0][0]
    #result = betterH[-1][0]
    if result == '':
        return 'ERROR', motivo # Isso vai acontecer quando não acharmos uma posição válida par ao horário, e nesse caso toda a grade de horários dessa possibilidade não pode ser usada
    else:
        return f"{result};{turm[0]}", 0  # Retorna f'{day};{hour};{turm}' depois nós colocaremos a room variable
                              # Se bimestral será: f'{day};{hour};{bimester};{turm}'


def cost_individual(horario, position, board, subjectPos, typeNum, sala='', bimestral=0):
    # Position => (Dia, horário, bimestre)
    points = loadData.getPoints('./data/preferencias.txt')
    pointsKeys = points.keys()

    pontuation = 0
    dayBoard = board[position[0]][typeNum]
    teacherDayBoard = horario.teacher.schedule[position[0]][typeNum]

    horariosPreenchidos = 0  # Horarios já preenchidos no dia
    horariosP = 0  # Horarios já preenchidos no dia para os professores

    for p in pointsKeys:
        if p == "nHorariosDia":  # Para a quantidade de horários já preenchidos no dia
            for h in dayBoard:
                if h != 0:
                    if type(h) is list and bimestral == 1: # Condicionamento de bimestral
                        if ('1' == horario.type[2] and len(h) == 4) or ((not ('1' == horario.type[2])) and len(h) == 2) or ('4,G' in horario.type and len(h) == 3):
                            try:
                                if h[position[2]] != 0:
                                    horariosPreenchidos += 1
                                    pontuation += points[p]
                            except: 
                                pontuation -= 100                                
                    else:
                        horariosPreenchidos += 1
                        pontuation += points[p]
                    if type(h) is list:
                        for h_bimestral in h:
                            if h_bimestral:
                                if h_bimestral.local == horario.local:
                                    pontuation += points['MesmoCampus']
                    else:
                        if h.local == horario.local:
                            pontuation += points['MesmoCampus']

            for h in teacherDayBoard:
                if h != 0:
                    if type(h) is list and bimestral == 1: # Condicionamento de bimestral
                        if ('1' == horario.type[2] and len(h) == 4) or ((not ('1' == horario.type[2])) and len(h) == 2) or ('4,G' in horario.type and len(h) == 3):
                            if h[position[2]] != 0:
                                horariosPreenchidos += 1
                                pontuation += points[p]
                    else:
                        horariosP += 1
                        pontuation += points[p]

        elif p == "tresHorariosDia":
            if horariosPreenchidos >= 3: pontuation += points[p]  # Da turma
            if horariosP >= 3: pontuation += points[p]  # Do professor

        elif p == "horariosPoints": # Horários finais e iniciais do dia (piores horários para alunos e professores)
            if position[1] in [0, 5] and typeNum != 2:
                pontuation += points[p]
            elif typeNum == 2:
                position[1] == 3
                pontuation += points[p]

        elif p == "lastResp": # Se o horário for ao lado de outro da mesma matéria
            if position[1] != 0:
                if dayBoard[position[1] - 1] != 0:
                    if bimestral == 1 and type(dayBoard[position[1] - 1]) is list:
                        try:
                            if dayBoard[position[1] - 1][position[2]] != 0: # se não está vázio
                                if dayBoard[position[1] - 1][position[2]].subject == horario.subject: 
                                    pontuation += points[p] *2
                        except: pass
                    else:
                        try:
                            if dayBoard[position[1] - 1].subject == horario.subject: pontuation += points[p]
                        except: pass # Pode ocorrer caso o outro horário seja de lista (bimestral)
            if not(position[1] == 5 or (position[1] == 3 and typeNum == 2)):
                if dayBoard[position[1] + 1] != 0:
                    if bimestral == 1 and type(dayBoard[position[1] + 1]) is list:
                        try:
                            if dayBoard[position[1] + 1][position[2]] != 0: # se não está vázio
                                if dayBoard[position[1] + 1][position[2]].subject == horario.subject:      # Não está levando em consideração que o próximo horário pode não ter a mesma quantidade de 
                                    pontuation += points[p] *2
                        except: pass
                    else:
                        try:
                            if dayBoard[position[1] + 1].subject == horario.subject: pontuation += points[p]
                        except: pass # Pode ocorrer caso o outro horário seja de lista (bimestral)
                        
        elif p == "bimestraisJuntos" and bimestral and type(dayBoard[position[1]]) is list:
            pontuation += points[p]
        elif p == "Espaco_no_mesmo_lugar":
            for h in range(0, len(dayBoard)):
                if not(dayBoard[h]) and not(horario.teacher.schedule[position[0]][typeNum][h]):
                    pontuation += points[p]
        
        """
        elif p == "preferPositiva":  # negativa e positiva para diminuir código
            for prefer in horario.teacher.prefers[subjectPos]:  # para cada limitação do professor
                if f'N{position[0]}' in str(prefer) or f'S{position[0]}' in str(prefer):  # Se a limitação estiver no dia do horário
                    try:
                        limite_inferior = int(prefer.split(':')[1].split(',')[0])
                        limite_superior = int(prefer.split(':')[1].split(',')[1])
                        if typeNum == 1: # tarde, diminui em 6 para a avaliação dentro apenas do turno
                            limite_inferior -= 6
                            limite_superior -= 6
                    except:  # Considerando o caso de não ter selecionado uma variação de horários
                        limite_inferior = 1
                        limite_superior = 12

                    if (limite_inferior <= int(position[1]) + 1) and (limite_superior >= int(
                            position[1]) + 1):  # Se o horário estiver compreendido durante a limitação
                        if str(prefer)[0] == 'S':
                            pontuation += points['preferPositiva']
                        else:
                            pontuation += points['preferNegativa']
        """

        # Se o horário for bimestral e tiver uma lista na posição em que ele será colocado
        

    return pontuation


def cost_board(board):
    n_h_bimestrais = 0
    # Vamos calcular uma vez para cada bimestre como se fosse um quadr a parte
    points = loadData.getPoints('./data/preferencias.txt')

    media = 0

    spaces = 4 # vai possuir valores diferentes dependendo do tipo do horário
               # Se o horário for 1 bimestre, vai ser 4, se for 2 vai ser 2, se for 4 vai ser 2 também
    for b in range(0, spaces): # Para cada bimestre
        # Vamos ir somando valores a result_value conforme vamos aumentando a pontuação
        result_value = 0 
        for quadro in board.values():  # Para cada turma
            for day in quadro.values():  # Para cada dia nesta turma
                typeNum = 0 # qual turno (0 manhã, 1 tarde)
                for turno in day:  # Para cada turno desse dia
                    # Começamos contando o número de zeros, ou seja, de horários vagos
                    num_of_0 = 0

                    for h in turno:
                        if type(h) is list:
                            for bimestral in h:
                                if bimestral == 0:
                                    num_of_0 += 1
                                else:
                                    result_value = result_value + points['bimestraisJuntos'] if bimestral != 0 else result_value
                        elif h == 0:
                            num_of_0 += 1
                    # Pontuação para cada dia já preenchido
                    result_value += (6 - num_of_0) * points['nHorariosDia']

                    # Pontuação para mais de 3 horários já preenchidos no mesmo dia
                    if num_of_0 < 3:
                        result_value += points['tresHorariosDia']

                    # Primeiros e últimos horários do turno
                    
                    if turno[0] != 0:
                        result_value += points['horariosPoints']

                    elif type(turno[0]) is list:
                        result_value += points['horariosPoints']
                    
                    if turno[-1] != 0:
                        result_value += points['horariosPoints']
                    
                    elif type(turno[-1]) is list:
                        result_value += points['horariosPoints']
                    
                    # Horários de mesma matéria agrupados
                    for h in range(0, len(turno)-1):
                        #if (h != len(turno) - 1):
                        if turno[h] != 0 and turno[h+1] != 0:
                            if not(type(turno[h]) is list or type(turno[h+1]) is list) and turno[h] != 0 and turno[h+1] != 0:
                                if turno[h].subject == turno[h+1].subject:
                                    result_value += points['lastResp']
                            elif (type(turno[h]) is list) and (type(turno[h+1]) is list) and b == 0:
                                if len(turno[h]) == len(turno[h+1]):
                                    for count in range(0, len(turno[h])):
                                        if turno[h][count] and turno[h+1][count]:
                                            if turno[h][count].subject == turno[h+1][count].subject:
                                                result_value += points['lastResp']                                
                    
                    # Professor dando aula no dia que ele quer
                    
                    for h in range(0, len(turno)):
                        if turno[h] != 0 and not(type(turno[h]) is list):
                            hor = turno[h]
                        elif type(turno[h]) is list:
                            for count in range(0, len(turno[h])):
                                hor = turno[h][count]
                                if hor:
                                    for prefers in hor.teacher.prefers:
                                        for p in prefers:  # para cada limitação do professor
                                            if f'N{day}' in str(p) or f'S{day}' in str(p):  # Se a limitação estiver no dia do horário
                                                try:
                                                    limite_inferior = int(p.split(':')[1].split(',')[0])
                                                    limite_superior = int(p.split(':')[1].split(',')[1])

                                                    # O horário 1 do turno da tarde equivale ao horário 7 no quadro geral, assim, 
                                                    # precisamos subtrair esses valores para que faça sentido na lista em que estão inseridos
                                                    if typeNum == 1:
                                                        limite_inferior -= 6
                                                        limite_superior -= 6
                                                    elif typeNum == 2:
                                                        limite_inferior -= 12
                                                        limite_superior -= 12
                                                except:  # Considerando o caso de não ter selecionado uma variação de horários
                                                    limite_inferior = 1
                                                    limite_superior = 12

                                                if (limite_inferior <= int(h) + 1) and (limite_superior >= int(h) + 1):  # Se o horário estiver compreendido durante a limitação
                                                    if str(p)[0] == 'S':
                                                        result_value += points['preferPositiva']
                                                    else:
                                                        result_value += points['preferNegativa']
                            if hor:
                                for prefers in hor.teacher.prefers:
                                    for p in prefers:  # para cada limitação do professor
                                        if f'N{day}' in str(p) or f'S{day}' in str(p):  # Se a limitação estiver no dia do horário
                                            try:
                                                limite_inferior = int(p.split(':')[1].split(',')[0])
                                                limite_superior = int(p.split(':')[1].split(',')[1])

                                                # O horário 1 do turno da tarde equivale ao horário 7 no quadro geral, assim, 
                                                # precisamos subtrair esses valores para que faça sentido na lista em que estão inseridos
                                                if typeNum == 1:
                                                    limite_inferior -= 6
                                                    limite_superior -= 6
                                                elif typeNum == 2:
                                                    limite_inferior -= 12
                                                    limite_superior -= 12
                                            except:  # Considerando o caso de não ter selecionado uma variação de horários
                                                limite_inferior = 1
                                                limite_superior = 12

                                            if (limite_inferior <= int(h) + 1) and (limite_superior >= int(h) + 1):  # Se o horário estiver compreendido durante a limitação
                                                if str(p)[0] == 'S':
                                                    result_value += points['preferPositiva']
                                                else:
                                                    result_value += points['preferNegativa']
                                                    
                    typeNum += 1
        media += result_value
    return (media/4)



def validation(horario, position, board, subjectPos, typeNum, sala='', bimestral=0):  # board é o quadro de horários
    """
    Vemos se um determinado horário pode ser colocado em uma determinada posição
    Umas das funções mais usadas, sua eficiência é bem mais importante que as das demais.
    """
    # Position = [day, hour]
    INVALIDO = -99
    BREAK_INVALIDO = -100 # para parar loops em analises bimestrais

    # h_room = sala    # Sala
    h_day = position[0]   # Dia
    h_time = position[1]  # Horário

    if typeNum == 2 and h_time >= 4:
        print('Mais horários do que devia', horario, h_time)

    # Limitações do professor
    limitation = horario.teacher.limits[subjectPos]
    t_limitations = []  # N3:1,4
    """
    for l in limitation:  # para cada limitação do professor
        if f'N{h_day}' in str(l):  # Se a limitação estiver no dia do horário
            try:
                limite_inferior = int(l.split(':')[1].split(',')[0])
                limite_superior = int(l.split(':')[1].split(',')[1])
                if typeNum == 1:
                    limite_inferior -= 6
                    limite_superior -= 6
                elif typeNum == 2:
                    limite_inferior -= 12
                    limite_superior -= 12
            except:  # Considerando o caso de não ter selecionado uma variação de horários
                limite_inferior = 1
                limite_superior = 12

            if (limite_inferior <= int(h_time) + 1) and (limite_superior >= int(h_time) + 1):  # Se o horário estiver compreendido durante a limitação
                return INVALIDO, 'LIMITAÇÃO DO PROFESSOR ________'
    """
    # Limitações da sala
    # room_invalids_h =

    # Horário já está ocupado por outro no Quadro de horários?
    if not('2' in board.keys()):
        print(board.keys())
    if board[str(h_day)][typeNum][h_time] != 0: # Se horário preenchido 
        if type(board[str(h_day)][typeNum][h_time]) is list and horario.teacher.bimestral[subjectPos] == 1: # Se horário preenchido for lista e o horário for bimestral
            if len(board[str(h_day)][typeNum][h_time]) == 4:
                if board[str(h_day)][typeNum][h_time][position[2]] != 0:
                    return INVALIDO, 'HORÁRIO JÁ OCUPADO 2 _________'
                for outros_horarios in board[str(h_day)][typeNum][h_time]:
                    if outros_horarios:
                        if outros_horarios.type != horario.type:
                            return INVALIDO, f'HORÁRIO POSSUI TIPO DIFERENTE DOS DEMAIS _{outros_horarios.type, horario.type}'
                        if outros_horarios.subject == horario.subject:
                            return INVALIDO, f'MESMA MATÉRIA FICA EM LISTAS DIFERENTES _{outros_horarios.subject, horario.subject}'
            # Se horário estiver preenchido
            else:
                for outros_horarios in board[str(h_day)][typeNum][h_time]:
                    if outros_horarios:
                        # Se os outros horários da lista forem de tipos diferentes
                        if outros_horarios.type != horario.type or ('3,1,G' in horario.type and len(board[str(h_day)][typeNum][h_time]) != 4):
                            return INVALIDO, f'HORÁRIO POSSUI TIPO DIFERENTE DOS DEMAIS _{outros_horarios.type, horario.type}'
                        
                if board[str(h_day)][typeNum][h_time][position[2]] != 0:
                    return INVALIDO, 'HORÁRIO JÁ OCUPADO 2 _________'

        else: 
            return BREAK_INVALIDO, f'HORÁRIO JÁ OCUPADO 3 _tem um normal no lugar: {horario.type}'
    
    # Verificar também a parte dos professores
    if type(horario.teacher.schedule[str(h_day)][typeNum]) is int:
        print(horario, horario.teacher.schedule, horario.teacher.schedule[str(h_day)])
    if horario.teacher.schedule[str(h_day)][typeNum][h_time] != 0: # Se horário preenchido 
        if type(horario.teacher.schedule[str(h_day)][typeNum][h_time]) is list and horario.teacher.bimestral[subjectPos] == 1: # Se horário preenchido for lista e o horário for bimestral
            if not(0 in horario.teacher.schedule[str(h_day)][typeNum][h_time]):
                return BREAK_INVALIDO, 'HORÁRIO JA OCUPADO PROFESSORES 1 _______'
            
            # Se horário estiver preenchido
                #Precisamos antes checar se as condições do horário estão corretas, se é compatível o horário que estamos colocando com o local em que ele será colocado
            if (len(horario.teacher.schedule[str(h_day)][typeNum][h_time]) == 4 and '1' == horario.type[2]) or (len(horario.teacher.schedule[str(h_day)][typeNum][h_time]) == 2 and '2,T' in horario.type) or (len(horario.teacher.schedule[str(h_day)][typeNum][h_time]) == 3 and '4,G' in horario.type):
                try: 
                    if horario.teacher.schedule[str(h_day)][typeNum][h_time][position[2]] != 0:
                        return INVALIDO, 'HORÁRIO JA OCUPADO PROFESSORES 2 _______'
                except:
                    print('Posição e horário não estão de acordo', position[2], horario.type)
                    if horario.teacher.schedule[str(h_day)][typeNum][h_time][position[2]] != 0:
                        pass

        else: 
            return BREAK_INVALIDO, 'HORÁRIO JA OCUPADO PROFESSORES 3 _______'

    # Não pode trabalhar mais de 8h no mesmo dia
    horaries_in_day = horario.teacher.schedule[position[0]]
    bimestral_h = [] # horários bimestrais
    num_h = 0 # numero de horários
    for h in horaries_in_day:
        if type(h) is list:
            bimestral_h.append(h)
        elif h != 0:
            num_h += 1
    max_value = 0
    for c in range(0, 4):
        num_h_bimestral = 0
        for h in bimestral_h:
            if h[c] != 0:
                num_h_bimestral += 1
        max_value = num_h_bimestral if num_h_bimestral >= max_value else max_value
    num_h = num_h + max_value
    if num_h >= 10:
        return INVALIDO, 'MAIS DE 8H DE POR DIA ____________'

    # Se tiver um horário de campus diferente no mesmo turno, manhã ou tarde, ele não pode existir: 
    # juntar os horários de um mesmo campûs em um mesmo momento de manhã ou tarde
    for h in board[position[0]]:
        for value in h:
            if value != 0:
                if type(value) is list:
                    for b in value:
                        if b != 0:
                            if type(b) is list: print('B é do tipo lista: ', board[position[0]])
                            if horario.local != b.local:
                                return INVALIDO, 'CAMPUS DIFERENTES EM UM MESMO TURNO 1 __________'

                elif horario.local != value.local:
                    return INVALIDO, 'CAMPUS DIFERENTES EM UM MESMO TURNO 2 __________'

    # Não pode ter um intervalo entre uma aula e outra maior que 3h

    # Devem ser ao menos 11h entre o primeiro e o último horário de descanso
    # Status: aguardando reunião, atualmente seria impossível o estado acima citado não ser válido
    #print('Resultado aprovado -> ', board[str(h_day)][typeNum][h_time], position)
    return 0, 'Tudo certo :)'


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
            bimestre = []
            for d in range(0, 4):
                v = (d + c) % 4
                bimestre.appned(lista_b[v])
            result.append(bimestre)
        return result
    for h in lista_b:
        if h != 0:
            if '2' in h.tipo:
                return [[lista_b[0], lista_b[1]], [lista_b[1], lista_b[0]]]
            elif '4' in h.tipo:
                return lista_b
            else:
                print('ERROR: Tipo do horário não corresponde a nenhum dos requisitos')
            

def replace_h(quadro, turma, turno, h1, d1, p1, h2, d2, p2,positions_for_horaries, pb_1='Nada', pb_2='Nada'):
    """
    Dados 2 horários, trocamos eles de posição
    """


    print('replace_h', end=' ')
    for p in positions_for_horaries:
        try:
            if quadro[turma][p[0]][turno][p[1]]:
                if quadro[turma][p[0]][turno][p[1]][p[2]]:
                    if not(str(quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]]).split('-')[-1] in str(quadro[turma][p[0]][turno][p[1]][p[2]])) or not(quadro[turma][p[0]][turno][p[1]][p[2]]):
                        print('H1 não é o mesmo para professor')
                        break
                else:
                    try:
                        if not(str(quadro[turma][p[3]][turno][p[4]][p[5]].teacher.schedule[p[3]][turno][p[4]][p[5]]).split('-')[-1] in str(quadro[turma][p[3]][turno][p[4]][p[5]])):
                            print('H2 não é o mesmo para professor')
                            break
                    except: pass
        except:
            if quadro[turma][p[0]][turno][p[1]]:
                if not(str(quadro[turma][p[0]][turno][p[1]].teacher.schedule[p[0]][turno][p[1]]).split('-')[-1] in str(quadro[turma][p[0]][turno][p[1]])) or not(quadro[turma][p[0]][turno][p[1]]):
                    print('H1, normal, está no lugar errado')
                    break
                else:
                    try:
                        if not(str(quadro[turma][p[3]][turno][p[4]].teacher.schedule[p[3]][turno][p[4]]).split('-')[-1] in str(quadro[turma][p[3]][turno][p[4]])):
                            print('H2, normal, está no lugar errado')
                            break
                    except: pass
    if pb_1 != 'Nada':
        
        if type(quadro[turma][d1][turno][p1]) is list:
            quadro[turma][d1][turno][p1][pb_1] = h2
        else:
            if '1' == h2.type[1]:
                if not(quadro[turma][d1][turno][p1]): quadro[turma][d1][turno][p1] = [0, 0, 0, 0]
            elif '4,G' in h2.type:
                if not(quadro[turma][d1][turno][p1]): quadro[turma][d1][turno][p1] = [0, 0, 0]
            else:
                if not(quadro[turma][d1][turno][p1]): quadro[turma][d1][turno][p1] = [0, 0]
            # Colocamos o horário na posição
            quadro[turma][d1][turno][p1][pb_1] = h2

        if type(quadro[turma][d2][turno][p2]) is list:
            quadro[turma][d2][turno][p2][pb_2] = h1
        else:
            if '1' == h1.type[2]:
                if not(quadro[turma][d2][turno][p2]): quadro[turma][d2][turno][p2] = [0, 0, 0, 0]
            elif '4,G' in h1.type:
                if not(quadro[turma][d2][turno][p2]): quadro[turma][d2][turno][p2] = [0, 0, 0]
            else:
                if not(quadro[turma][d2][turno][p2]): quadro[turma][d2][turno][p2] = [0, 0]
            # Colocamos o horário na posição
            quadro[turma][d2][turno][p2][pb_2] = h1
        
        if type(h1.teacher.schedule[d2][turno][p2]) is list:
            h1.teacher.schedule[d2][turno][p2][pb_2] = h1
            #print('colocando h1 com lista')
        else:
            if '1' == h1.type[2]:
                if not(h1.teacher.schedule[d2][turno][p2]): h1.teacher.schedule[d2][turno][p2] = [0, 0, 0, 0]
            elif '4,G' in h1.type:
                if not(h1.teacher.schedule[d2][turno][p2]): h1.teacher.schedule[d2][turno][p2] = [0, 0, 0]
            else:
                if not(h1.teacher.schedule[d2][turno][p2]): h1.teacher.schedule[d2][turno][p2] = [0, 0]
            # Colocamos o horário na posição
            h1.teacher.schedule[d2][turno][p2][pb_2] = h1
            #print('colocando h1, []') #print(h1.teacher.schedule[d2][turno][p2][pb_2] == h1)
        if h2: # Se h2 não for 0
            if type(h2.teacher.schedule[d1][turno][p1]) is list:
                h2.teacher.schedule[d1][turno][p1][pb_1] = h2
                #print('colocando h2, com lista')
            else:
                if '1' == h2.type[1]:
                    if not(h2.teacher.schedule[d1][turno][p1]): h2.teacher.schedule[d1][turno][p1] = [0, 0, 0, 0]
                elif '4,G' in h2.type:
                    if not(h2.teacher.schedule[d1][turno][p1]): h2.teacher.schedule[d1][turno][p1] = [0, 0, 0]
                else:
                    if not(h2.teacher.schedule[d1][turno][p1]): h2.teacher.schedule[d1][turno][p1] = [0, 0]
                # Colocamos o horário na posição
                h2.teacher.schedule[d1][turno][p1][pb_1] = h2
                #print('colocando h2, []')  #print(h2.teacher.schedule[d1][turno][p1][pb_1] == h2)

        
    

    else: # Ambos os horários são normais
        print('Era para passar por aqui? ', pb_1 == 'Nada', end=' ')
        quadro[turma][d1][turno][p1] = h2
        quadro[turma][d2][turno][p2] = h1
        h1.teacher.schedule[d2][turno][p2] = h1
        try: h2.teacher.schedule[d1][turno][p1] = h2
        except: pass   # Pode acontecer caso h2 seja 0
    try:
        if  h1.teacher.schedule[d2][turno][p2][pb_2] != h1 or h2.teacher.schedule[d1][turno][p1][pb_1] != h2:
            print('Saindo errado do replace_h')
    except:
        if h1.teacher.schedule[d2][turno][p2] != h1:
            try: 
                if h2.teacher.schedule[d1][turno][p1] == h2:
                    print('Normal saindo errado do replace')
            except: pass   # Pode acontecer caso h2 seja 0

        

def print_quadro(quadro, horario, typeNum):
    print('========== PROFESSOR')
    for variavel in horario.teacher.schedule.values():
        print(len(variavel), end=' ')
        print('[', end='')
        for value in variavel[typeNum]:
            if value:
                if type(value) is list:
                    print('[', end='')
                    for bimestre in value:
                        if bimestre: print('X', end=', ')
                        else: print(' ', end=', ')
                    print(']', end=', ')
                else:
                    print('X', end=', ')
                
            else: print(' ', end=', ')
        print(' ]')
    print('========== SALA', horario.turm)
    for variavel in quadro[horario.turm[0]].values():
        print('[', end='')
        for value in variavel[typeNum]:
            if value:
                if type(value) is list:
                    print('[', end='')
                    for bimestre in value:
                        if bimestre: print('X', end=', ')
                        else: print(' ', end=', ')
                    print(']', end=', ')
                else:
                    print('X', end=', ')
                
            else: print(' ', end=', ')
        print(' ]')
    

def days_with_zero(quadro, turno, h):
    """
    Vamos criar uma lista com apenas os dias que possuem 0, e vamos fazer com que o programa dê preferência para eles
    """
    result = []
    for dia, horarios in quadro[h.turm[0]].items():
        for horario in horarios[turno]:
            if horario == 0:
                result.append(dia)
            elif type(horario) is list:
                for bimestral in horario:
                    if not(bimestral):
                        result.append(dia)
                        break
    return result
            

def generate_list_position(quadro, turno, turma):
    """
    Vamos criar uma lista com todos os possíveis conjuntos de valores que h1 e h2 podem ter
    h1 não pode ser 0
    h2 tem que ser do mesmo tipo que h1
    """
    print('generating list...')
    result = []
    for dia_1 in range(2, 7):
        dia_1 = str(dia_1)
        if quadro[turma][dia_1].count(0) == len(quadro[turma][dia_1]):
            continue
        for dia_2 in range(2, 7):
            dia_2 = str(dia_2)
            for p1 in range(0, len(quadro[turma][dia_1][turno])):
                if quadro[turma][dia_1][turno][p1] == 0:
                    continue
                elif type(quadro[turma][dia_1][turno][p1]) is list:
                    # Se acharmos um pb_1 que não é 0, temos que então achar um pb_2
                    for pb1 in range(0, len(quadro[turma][dia_1][turno][p1])):
                        if quadro[turma][dia_1][turno][p1][pb1] == 0:
                            continue
                        for p2 in range(0, len(quadro[turma][dia_1][turno])):
                            if type(quadro[turma][dia_2][turno][p2]) is list:
                                if len(quadro[turma][dia_2][turno][p2]) == len(quadro[turma][dia_1][turno][p1]):
                                    for pb2 in range(0, len(quadro[turma][dia_2][turno][p2])):
                                        if not(quadro[turma][dia_2][turno][p2][pb2]):
                                            result.append((dia_1, p1, pb1, dia_2, p2, pb2))
                                            if quadro[turma][dia_1][turno][p1][pb1] == 0:
                                                print('Estamos adicionando um h1 == 0')
                                        elif quadro[turma][dia_2][turno][p2][pb2].type != quadro[turma][dia_1][turno][p1][pb1].type:
                                            break
                                        elif quadro[turma][dia_2][turno][p2][pb2] == quadro[turma][dia_1][turno][p1][pb1]:
                                            pass
                                        else:
                                            result.append((dia_1, p1, pb1, dia_2, p2, pb2))
                                            if quadro[turma][dia_1][turno][p1][pb1] == 0:
                                                print('Estamos adicionando um h1 == 0')
                                            if len(quadro[turma][dia_2][turno][p2]) != len(quadro[turma][dia_1][turno][p1]):
                                                print('GENERATE LIST - Eles são de tamanhos diferentes: ', quadro[turma][dia_2][turno][p2], quadro[turma][dia_1][turno][p1])
                            elif not(quadro[turma][dia_2][turno][p2]): # Caso selecionemos um horário vazio que nem tenha uma lista nele.
                                pb2 = random.randint(0, len(quadro[turma][dia_1][turno][p1])-1)
                                result.append((dia_1, p1, pb1, dia_2, p2, pb2))
                                if quadro[turma][dia_1][turno][p1][pb1] == 0:
                                    print('Estamos adicionando um h1 == 0')
                else: # Se h1 for normal, temos que selecionar um h2 normal
                    for p2 in range(0, len(quadro[turma][dia_1][turno])):
                        if not(type(quadro[turma][dia_2][turno][p2]) is list):
                            result.append((dia_1, p1, dia_2, p2))
                            if quadro[turma][dia_1][turno][p1] == 0:
                                print('Estamos adicionando um h1 == 0, normal')
    for p in result:
                try:
                    if quadro[turma][p[0]][turno][p[1]][p[2]]:
                        if not(str(quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]]).split('-')[-1] in str(quadro[turma][p[0]][turno][p[1]][p[2]])) or not(quadro[turma][p[0]][turno][p[1]][p[2]]):
                            print('GENERATING', quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]], quadro[turma][p[0]][turno][p[1]][p[2]])
                            break
                    else:
                        try:
                            if not(str(quadro[turma][p[3]][turno][p[4]][p[5]].teacher.schedule[p[3]][turno][p[4]][p[5]]).split('-')[-1] in str(quadro[turma][p[3]][turno][p[4]][p[5]])):
                                print('GENERATING', quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]], quadro[turma][p[0]][turno][p[1]][p[2]])
                                break
                        except: pass
                except:
                    if not(str(quadro[turma][p[0]][turno][p[1]].teacher.schedule[p[0]][turno][p[1]]).split('-')[-1] in str(quadro[turma][p[0]][turno][p[1]])) or not(quadro[turma][p[0]][turno][p[1]]):
                        print('GENERATING', quadro[turma][p[0]][turno][p[1]].teacher.schedule[p[0]][turno][p[1]][p[2]], quadro[turma][p[0]][turno][p[1]][p[2]])
                        break
                    else:
                        try:
                            if not(str(quadro[turma][p[3]][turno][p[4]].teacher.schedule[p[3]][turno][p[4]]).split('-')[-1] in str(quadro[turma][p[3]][turno][p[4]])):
                                print('GENERATING', quadro[turma][p[0]][turno][p[1]].teacher.schedule[p[0]][turno][p[1]][p[2]], quadro[turma][p[0]][turno][p[1]][p[2]])
                                break
                        except: pass
    return result
                                
                        
def actualize_list_posittions(quadro, turma, turno, lista, d1, p1, d2, p2, pb1=None, pb2=None):
    """
    Quando mudamos dois horários de posição, as respectivas posições para as quais tinhamos uma possível mudança passam a ser inválidas
    Vamos encontrar todas as posições que correspondiam ao h1 que mudamos, bem como todas que correspondiam ao h2 que mudamos
    Vamos pegar essa posição antiga e trocar por uma com a nova posição, vamos apagar a posição(d1, p1, d3, p3) e colocar outra (d2, p2, d3, p3)
    Se o segundo horário for 0, não podemos ter um 0 na primeira metade
    (d2 e p2) novas posições do horário 1
    (d1 e p1) novas posições do horario 2
    """
    print('actualize list ...', end='')
    if type(quadro[turma][d2][turno][p2]) is list:
        if quadro[turma][d2][turno][p2][pb2].teacher.schedule[d2][turno][p2].count(0) == len(quadro[turma][d2][turno][p2][pb2].teacher.schedule[d2][turno][p2]):
            quadro[turma][d2][turno][p2][pb2].teacher.schedule[d2][turno][p2] = 0
        try:
            if quadro[turma][d1][turno][p1][pb1].teacher.schedule[d1][turno][p1].count(0) == len(quadro[turma][d1][turno][p1][pb1].teacher.schedule[d1][turno][p1]):
                quadro[turma][d1][turno][p1][pb1].teacher.schedule[d1][turno][p1] = 0
        except: pass
    
    try:
        if quadro[turma][d2][turno][p2][pb2] == 0:
            print('Já chegou errado para atualizar')
    except:
        if quadro[turma][d2][turno][p2] == 0:
            print('Já chegou errado para atualizar esse normal: ', quadro[turma][d2][turno][p2], pb1)
    n_zeros_normais = 0
    n_zeros_bimestrais = 0
    valores_a_serem_acrescentados = []
    valores_a_serem_removidos = []
    for valor in lista:
        if len(valor) == 4 and pb1 == None:
            if quadro[turma][valor[0]][turno][valor[1]] == 0:
                n_zeros_normais += 1
                first_is_zero = True
            if (valor[0] == d1) and (valor[1] == p1): # Achamos um:
                if quadro[turma][d2][turno][p2] == 0:
                    print('Adicionando 0 na hora de trocar 1 -> 2')
                valores_a_serem_acrescentados.append((d2, p2, valor[2], valor[3]))
                valores_a_serem_removidos.append(valor)
            elif(valor[2] == d1) and (valor[3] == p1):
                valores_a_serem_acrescentados.append((valor[0], valor[1], d2, p2))
                valores_a_serem_removidos.append(valor)
            elif (valor[0] == d2) and (valor[1] == p2): # Achamos um:
                if quadro[turma][d1][turno][p1] == 0:
                    print('Adicionando 0 na hora de trocar 2 -> 1')
                valores_a_serem_acrescentados.append((d1, p1, valor[2], valor[3]))
                valores_a_serem_removidos.append(valor)
            elif(valor[2] == d2) and (valor[3] == p2):
                valores_a_serem_acrescentados.append((valor[0], valor[1], d1, p1))
                valores_a_serem_removidos.append(valor)
        elif len(valor) == 6 and pb1 != None:
            # Se tivermos alguma posição com uma lista vazia, transformamos ela em apenas 0 para podermos colocar qualquer horário ali.
            if quadro[turma][valor[3]][turno][valor[4]]:
                
                if quadro[turma][valor[3]][turno][valor[4]].count(0) == len(quadro[turma][valor[3]][turno][valor[4]]):
                    quadro[turma][valor[3]][turno][valor[4]] = 0
                # Essa Nova posição ainda não está sendo acrescentada
                    for positions in lista:
                        if not((positions[0], positions[1], positions[2], valor[3], valor[4], valor[5]) in lista) and not((positions[0], positions[1], positions[2], valor[3], valor[4], valor[5]) in valores_a_serem_acrescentados):
                            valores_a_serem_acrescentados.append((positions[0], positions[1], positions[2], valor[3], valor[4], valor[5]))
                

            if (valor[0] == d1) and (valor[1] == p1) and (valor[2] == pb1):
                valores_a_serem_acrescentados.append((d2, p2, pb2, valor[3], valor[4], valor[5]))
                valores_a_serem_removidos.append(valor)
            elif (valor[3] == d1) and (valor[4] == p1) and (valor[5] == pb1):
                valores_a_serem_acrescentados.append((valor[0], valor[1], valor[2], d2, p2, pb2))
                valores_a_serem_removidos.append(valor)

            elif (valor[0] == d2) and (valor[1] == p2) and (valor[2] == pb2):
                valores_a_serem_acrescentados.append((d1, p1, pb1, valor[3], valor[4], valor[5]))
                valores_a_serem_removidos.append(valor)
            elif (valor[3] == d2) and (valor[4] == p2) and (valor[5] == pb2):
                valores_a_serem_acrescentados.append((valor[0], valor[1], valor[2], d1, p1, pb1))
                valores_a_serem_removidos.append(valor)
    for valor in valores_a_serem_removidos:
        lista.remove(valor)
    
    for p in lista:
        try:
            if quadro[turma][p[0]][turno][p[1]][p[2]]:
                if not(str(quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]]).split('-')[-1] in str(quadro[turma][p[0]][turno][p[1]][p[2]])):
                    print('ERRO no actualize list')
                    break
            else:
                try:
                    if not(str(quadro[turma][p[3]][turno][p[4]][p[5]].teacher.schedule[p[3]][turno][p[4]][p[5]]).split('-')[-1] in str(quadro[turma][p[3]][turno][p[4]][p[5]])):
                        print('ERRO no actualize list')
                        break
                except: pass
        except:
            if not(str(quadro[turma][p[0]][turno][p[1]].teacher.schedule[p[0]][turno][p[1]]).split('-')[-1] in str(quadro[turma][p[0]][turno][p[1]])):
                print('ERRO no actualize list')
                break
            else:
                try:
                    if not(str(quadro[turma][p[3]][turno][p[4]].teacher.schedule[p[3]][turno][p[4]]).split('-')[-1] in str(quadro[turma][p[3]][turno][p[4]])):
                        print('ERRO no actualize list')
                        break
                except: pass
    return lista + valores_a_serem_acrescentados

def actualize(teachers, new_teachers):
    """
    Vamos pegar os valores dos objetos que estamos usando e atualizá-los em função dos objetos que encontramos
    """
    print('actualize...')
    for old in teachers:
        for new in new_teachers:
            if old.name == new.name:
                if old.schedule != new.schedule:
                    print('|', end=' ')
                    old.schedule = new.schedule
                    break




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
                for bimester in range(0, 4):
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
                        if h[position[2]] != 0:
                            horariosPreenchidos += 1
                            pontuation += points[p]
                    else:
                        horariosPreenchidos += 1
                        pontuation += points[p]
            for h in teacherDayBoard:
                if h != 0:
                    if type(h) is list and bimestral == 1: # Condicionamento de bimestral
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
                        if dayBoard[position[1] - 1][position[2]] != 0: # se não está vázio
                            if dayBoard[position[1] - 1][position[2]].subject == horario.subject: 
                                pontuation += points[p] *2
                    else:
                        try:
                            if dayBoard[position[1] - 1].subject == horario.subject: pontuation += points[p]
                        except: pass # Pode ocorrer caso o outro horário seja de lista (bimestral)
            if not(position[1] == 5 or (position[1] == 3 and typeNum == 2)):
                if dayBoard[position[1] + 1] != 0:
                    if bimestral == 1 and type(dayBoard[position[1] + 1]) is list:
                        if dayBoard[position[1] + 1][position[2]] != 0: # se não está vázio
                            if dayBoard[position[1] + 1][position[2]].subject == horario.subject: 
                                pontuation += points[p] *2
                    else:
                        try:
                            if dayBoard[position[1] + 1].subject == horario.subject: pontuation += points[p]
                        except: pass # Pode ocorrer caso o outro horário seja de lista (bimestral)

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
        # Se o horário for bimestral e tiver uma lista na posição em que ele será colocado
        elif p == "bimestraisJuntos" and bimestral and type(dayBoard[position[1]]) is list:
            pontuation += points[p] * 10
            #pontuation += points[p] * dayBoard[position[1]][position[2]].count(0)
            #pontuation += points[p] * horario.teacher.schedule[position[0]][typeNum][position[1]].count(0)
        # print(pontuation)

    return pontuation


def cost_board(board):
    n_h_bimestrais = 0
    # Vamos calcular uma vez para cada bimestre como se fosse um quadr a parte
    points = loadData.getPoints('./data/preferencias.txt')

    media = 0
    for b in range(0, 4): # Para cada bimestre
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
                                result_value = result_value + points['bimestraisJuntos'] if bimestral != 0 else result_value
                            if h[b] == 0:
                                num_of_0 += 1
                        elif h == 0:
                            num_of_0 += 1
                    # Pontuação para cada dia já preenchido
                    result_value += (6 - num_of_0) * points['nHorariosDia']

                    # Pontuação para mais de 3 horários já preenchidos no mesmo dia
                    if num_of_0 < 3:
                        result_value += points['tresHorariosDia']

                    # Primeiros e últimos horários do turno
                    if type(turno[0]) is list:
                        if turno[0][b] != 0:
                            result_value += points['horariosPoints']
                    elif turno[0] != 0:
                        result_value += points['horariosPoints']

                    if type(turno[-1]) is list:
                        if turno[-1][b] != 0:
                            result_value += points['horariosPoints']
                    elif turno[-1] != 0:
                        result_value += points['horariosPoints']

                    # Horários de mesma matéria agrupados
                    for h in range(0, len(turno)):
                        if (h != len(turno) - 1):
                            if turno[h] != 0 and turno[h+1] != 0:
                                actual = turno[h] if not(type(turno[h]) is list) else turno[h][b]
                                prox = turno[h+1] if not(type(turno[h+1]) is list) else turno[h+1][b]
                                if actual != 0 and prox != 0:
                                    if actual.subject == prox.subject:
                                        result_value += points['lastResp']
                    
                    # Professor dando aula no dia que ele quer
                    for h in range(0, len(turno)):
                        hor = turno[h] if not(type(turno[h]) is list) else turno[h][b]
                        if hor != 0:  # Horários do turno (manhã ou tarde)
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
    # Position = [day, hour]

    INVALIDO = -99
    BREAK_INVALIDO = -100 # para parar loops em analises bimestrais

    # h_room = sala    # Sala
    h_day = position[0]   # Dia
    h_time = position[1]  # Horário

    # Limitações do professor
    limitation = horario.teacher.limits[subjectPos]
    t_limitations = []  # N3:1,4

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

    # Limitações da sala
    # room_invalids_h =

    # Horário já está ocupado por outro no Quadro de horários?
    if board[str(h_day)][typeNum][h_time] != 0: # Se horário preenchido 
        if type(board[str(h_day)][typeNum][h_time]) == type(list()) and horario.teacher.bimestral[subjectPos] == 1: # Se horário preenchido for lista e o horário for bimestral

            if not(0 in board[str(h_day)][typeNum][h_time]):
                return BREAK_INVALIDO, 'HORÁRIO JÁ OCUPADO 1 _________'

            # Se horário estiver preenchido
            elif board[str(h_day)][typeNum][h_time][position[2]] != 0:
                return INVALIDO, 'HORÁRIO JÁ OCUPADO 2 _________'

        else: 
            return BREAK_INVALIDO, 'HORÁRIO JÁ OCUPADO 3 _________'

    # Verificar também a parte dos professores
    if horario.teacher.schedule[str(h_day)][typeNum][h_time] != 0: # Se horário preenchido 
        if type(horario.teacher.schedule[str(h_day)][typeNum][h_time]) == type(list()) and horario.teacher.bimestral[subjectPos] == 1: # Se horário preenchido for lista e o horário for bimestral
            if not(0 in horario.teacher.schedule[str(h_day)][typeNum][h_time]):
                return BREAK_INVALIDO, 'HORÁRIO JA OCUPADO PROFESSORES 1 _______'
            
            # Se horário estiver preenchido
            if horario.teacher.schedule[str(h_day)][typeNum][h_time][position[2]] != 0:
                return INVALIDO, 'HORÁRIO JA OCUPADO PROFESSORES 2 _______'

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
                if type(value) == type(list()):
                    for b in value:
                        if b != 0:
                            if horario.local != b.local:
                                return INVALIDO, 'CAMPUS DIFERENTES EM UM MESMO TURNO 1 __________'

                elif horario.local != value.local:
                    return INVALIDO, 'CAMPUS DIFERENTES EM UM MESMO TURNO 2 __________'

    # Não pode ter um intervalo entre uma aula e outra maior que 3h

    # Devem ser ao menos 11h entre o primeiro e o último horário de descanso
    # Status: aguardando reunião, atualmente seria impossível o estado acima citado não ser válido
    #print('Resultado aprovado -> ', board[str(h_day)][typeNum][h_time], position)
    return 0, 'Tudo certo :)'

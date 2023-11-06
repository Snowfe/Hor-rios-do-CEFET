# Arquivo com as funções envolvendo a lógica do nosso programa

import random
import copy
from functions import classes
from functions import loadData

"""
Regras Básicas:
- não mudar o board dentro das funções . Regra ignorada com suscesso kkkkk
"""


def getBetterHour(horario, board, subjectPos, typeNum):
    motivo = 0
    quadro = board.copy()
    if not('0' in horario.type):
        if '1' == horario.type[2]: n_bimestres = 4
        elif '4,G' in horario.type: n_bimestres = 3
        elif 'T' in horario.type: n_bimestres = 2
        else:
            raise Exception('Não corresponde a nenhum', horario, horario.type)
    betterH = [['', -999]]  # (day;hour, pontuação), melhores horários
    # Se for horário bimestral será (day;hour;bimestre, pontuação)

    teacher = horario.teacher
    turm = horario.turm
    subject = horario.subject
    motivos_do_erro = {}
    for d in range(2, 7):  # para cada dia
        d = str(d)
        n_horarios = 4 if typeNum == 2 else 6
        for h in range(0, n_horarios):  # para cada horário no dia
            if teacher.bimestral[subjectPos] == 0: # Se horário não for bimestral
                pontuation, motivo = validation(horario, [d, h], quadro, subjectPos, typeNum)

                # Vamos contando quantas vezes cada erro aconteceu.
                if not('OCUPADO' in motivo):
                    if not(motivo in motivos_do_erro.keys()):
                        motivos_do_erro[motivo] = 1 
                    else:
                        motivos_do_erro[motivo] += 1

                if pontuation == 0: # Se for válido
                    pontuation = cost_individual(horario, [d, h], quadro, subjectPos, typeNum)
                    if pontuation > betterH[0][1]:
                        betterH = [[f'{d};{h}', pontuation]]
                    elif pontuation == betterH[0][1]:
                        betterH.append([f'{d};{h}', pontuation])

            else: # Se for bimestral
                try:
                    n_bimestres += 1
                    n_bimestres -= 1
                except:
                    print(horario.type, horario.teacher.name, horario.turm)
                for bimester in range(0, n_bimestres):
                    pontuation, motivo = validation(horario, [d, h, bimester], quadro, subjectPos, typeNum, bimestral=1)
                    
                    # Vamos contando quantos erros ocorreram de cada tipo
                    if not('OCUPADO' in motivo):
                        if not(motivo in motivos_do_erro.keys()):
                            motivos_do_erro[motivo] = 1 
                        else:
                            motivos_do_erro[motivo] += 1

                    if pontuation == -100:
                        break #continue # Ou break?
                    if pontuation == 0:
                        pontuation = cost_individual(horario, [d, h, bimester], quadro, subjectPos, typeNum, bimestral=1)
                        if pontuation > betterH[0][1]:
                            betterH = [[f'{d};{h};{bimester}', pontuation]]
                        elif pontuation == betterH[0][1]:
                            betterH.append([f'{d};{h};{bimester}', pontuation])
                        
                        #print(pontuation, d, h, bimester)
    result = random.choice(betterH)[0]
    
    # Selecionamos qual o erro que aconteceu mais vezes
    maior = 0
    for m, n in motivos_do_erro.items():
        if maior <= n: 
            maior = n
            motivo = m
    
    if result == '':
        try: return 'ERROR', motivo # Isso vai acontecer quando não acharmos uma posição válida par ao horário, e nesse caso toda a grade de horários dessa possibilidade não pode ser usada
        except: 
            raise Exception(f'Não tem a moda do motivo {len(motivos_do_erro.values())}, {motivos_do_erro.values()}')
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
                        if ('1' == horario.type[2] and len(h) == 4) or (not('1' == horario.type[2]) and len(h) == 2) or ('4,G' in horario.type and len(h) == 3):
                            try:
                                if h[position[2]] != 0:
                                    horariosPreenchidos += 1
                                    pontuation += points[p]
                            except: 
                                pontuation -= 100                                
                    else:
                        horariosPreenchidos += 1
                        pontuation += points[p]
            
            for h in teacherDayBoard:
                if h != 0:
                    if type(h) is list and bimestral == 1: # Condicionamento de bimestral
                        if len(h) == 4 and horario.type[2] == '2':
                            pontuation += points['tipos_diferentes_separados']
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
                pontuation += points[p]/10
            elif typeNum == 2:
                position[1] == 3
                pontuation += points[p]/10

        elif p == "lastResp": # Se o horário for ao lado de outro da mesma matéria
            if position[1] != 0:
                if dayBoard[position[1] - 1] != 0:
                    if bimestral == 1 and type(dayBoard[position[1] - 1]) is list:
                        
                        # Vamos favorecer que os horários de um turno possuam um mesmo tipo
                        if type(dayBoard[position[1]]) is list:
                            if len(dayBoard[position[1] - 1]) == len(dayBoard[position[1]]):
                                pontuation += points[p]/2
                            else:
                                pontuation -= points[p]/2
                        else:
                            if (len(dayBoard[position[1] - 1]) == 4 and '1' == horario.type[2]) or (len(dayBoard[position[1] - 1]) == 3 and '4,G' in horario.type) or (len(dayBoard[position[1] - 1]) == 2 and not('1' == horario.type[2] or '4,G' in horario.type)):
                                pontuation += points[p]*2
                            else:
                                pontuation -= points[p]*2
                        try:
                            if dayBoard[position[1] - 1][position[2]] != 0: # se não está vázio
                                if dayBoard[position[1] - 1][position[2]].subject == horario.subject: 
                                    pontuation += points[p] *2
                                else:
                                    pontuation -= points[p]
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
                if type(dayBoard[h]) is list:
                    for bimestral in dayBoard[h]:
                        if bimestral:
                            if bimestral.local != horario.local:
                                pontuation += points[p]*5
        
        elif p == "Listas_iguais" and bimestral:
            for h in dayBoard:
                if type(h) is list:
                    if (len(h) == 4 and horario.type[2] == '1') or (len(h) == 3 and '4,G' in horario.type) or (len(h) == 2 and not('4,G' in horario.type or horario.type[2] == '1')):
                        pontuation += points[p]
        
        elif p == "Normais_juntos" and not(bimestral):
            for h in dayBoard:
                if h and not(type(h) is list):
                    if '0' in h.type:
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

def cost_board(board, typeNum=False, in_optimizer=False, teachers=[], novo_horario=0):
    n_h_bimestrais = 0
    # Vamos calcular uma vez para cada bimestre como se fosse um quadr a parte
    points = loadData.getPoints('./data/preferencias.txt')

    media = 0
    result_value = 0 
    spaces = 4 # vai possuir valores diferentes dependendo do tipo do horário
               # Se o horário for 1 bimestre, vai ser 4, se for 2 vai ser 2, se for 4 vai ser 2 também

    for t in teachers:
        for dia in t.schedule.keys():
            for turno in range(0, 3):
                # Vamos recompensar por horário vago
                result_value += t.schedule[dia][turno].count(0)**2 *points['Dia_vazio']/20

    for b in range(0, spaces): # Para cada bimestre
        # Vamos ir somando valores a result_value conforme vamos aumentando a pontuação
        
        for turma, quadro in board.items():  # Para cada turma
            
            if in_optimizer:
                
                # Vamos selecionar quais dias estão no mesmo campus que o campus do novo_horário
                dias_com_mesmo_campus = []
                dias_com_campus_diferentes = []
                zero_position = 5
                if turma == novo_horario.turm[0]: 
                    for dia in quadro.keys():
                        for position in range(0, len(quadro[dia][typeNum])):
                            if quadro[dia][typeNum][position]:
                                if type(quadro[dia][typeNum][position]) is list:
                                    if 0 in quadro[dia][typeNum][position]:
                                        if zero_position == 5: zero_position = quadro[dia][typeNum][position].index(0)
                                        elif zero_position == quadro[dia][typeNum][position].index(0):
                                            result_value = result_value + points['Dia_vazio'] if typeNum == 2 else result_value #+ points['Dia_vazio']/10
                                    
                                    for pb in range(0, len(quadro[dia][typeNum][position])):
                                        if quadro[dia][typeNum][position][pb]:
                                            if quadro[dia][typeNum][position][pb].local == novo_horario.local:
                                                dias_com_mesmo_campus.append(dia)
                                            else:
                                                dias_com_campus_diferentes.append(dia)
                                else:
                                    if quadro[dia][typeNum][position].local == novo_horario.local:
                                        dias_com_mesmo_campus.append(dia)
                                    else:
                                        dias_com_campus_diferentes.append(dia)
                for dia in dias_com_mesmo_campus:
                    if dia in dias_com_campus_diferentes: 
                        while dia in dias_com_campus_diferentes: dias_com_campus_diferentes.remove(dia)
                                        
                mais_zero = [0, 0]
                lista_dias = quadro.keys() if len(dias_com_campus_diferentes) == 0 else dias_com_campus_diferentes
                for day in lista_dias:
                    for turno in range(0, 3):
                        # Ainda não está de acordo no caso de empate
                        if mais_zero[1] < quadro[day][turno].count(0) or mais_zero[0] == 0:
                            mais_zero = [day, quadro[day][turno].count(0)]
                        elif mais_zero[1] == quadro[day][turno].count(0):
                            n_horarios_1 = 0
                            n_horarios_2 = 0
                            for c in range(0, len(quadro[day][turno])):
                                if type(quadro[day][turno][c]) is list:          n_horarios_1 += len(quadro[day][turno]) - quadro[day][turno][c].count(0)
                                if type(quadro[mais_zero[0]][turno][c]) is list: n_horarios_2 += len(quadro[mais_zero[0]][turno][c]) - quadro[mais_zero[0]][turno][c].count(0)

                            if n_horarios_1 < n_horarios_2:
                                mais_zero = [day, quadro[day][turno].count(0)]
                            
                selected_day = mais_zero[0]
                

            for day in quadro.values():  # Para cada dia nesta turma
                turno_preferencias = 0 # qual turno (0 manhã, 1 tarde)
                if in_optimizer:
                    if day == selected_day and not(day in dias_com_mesmo_campus):
                        result_value += points['Dia_vazio']*day.count(0)**2 * 1.5
                    else:
                        result_value += points['Dia_vazio']*day.count(0)**2
                else:
                    result_value += points['Dia_vazio']*day.count(0)**2
                
                for turno in day:  # Para cada turno desse dia
                    # Começamos contando o número de zeros, ou seja, de horários vagos
                    num_of_0 = 0

                    for h in turno:
                        if type(h) is list:
                            if in_optimizer and day == selected_day and not(day in dias_com_mesmo_campus): result_value += points['Dia_vazio']*h.count(0)**2/4
                            for bimestral in h:
                                if bimestral == 0: num_of_0 += 1
                                else: result_value = result_value + points['bimestraisJuntos'] * (len(h) - h.count(0))**2 if bimestral != 0 else result_value
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
                                    result_value = result_value + points['lastResp'] if not(in_optimizer) else result_value + points['lastResp']*5
                                else:
                                    result_value -= points['lastResp'] * 2
                            elif (type(turno[h]) is list) and (type(turno[h+1]) is list) and b == 0:
                                if len(turno[h]) == len(turno[h+1]):
                                    for count in range(0, len(turno[h])):
                                        if turno[h][count] and turno[h+1][count]:
                                            if turno[h][count].subject == turno[h+1][count].subject:
                                                result_value = result_value + points['lastResp'] if not(in_optimizer) else result_value + points['lastResp']*5
                                            else:
                                                result_value -= points['lastResp'] * 2
                                            
                        elif turno[h] == 0 and turno[h+1] == 0:
                            result_value += points['lastResp']/2                                
                    
                    # Professor dando aula no dia que ele quer
                    """
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
                                                    if turno_preferencias == 1:
                                                        limite_inferior -= 6
                                                        limite_superior -= 6
                                                    elif turno_preferencias == 2:
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
                                                if turno_preferencias == 1:
                                                    limite_inferior -= 6
                                                    limite_superior -= 6
                                                elif turno_preferencias == 2:
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
                    """
                    turno_preferencias += 1
        media += result_value
    return (result_value/4)



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

    """
    # Limitações do professor
    result, motivo = valid_limitations(horario, h_day, h_time, typeNum, subjectPos, INVALIDO)
    if result < 0: return result, motivo
    """
    # Vamos ver se o horário não pode ficar naquela posição por estarem em campus diferentes
    result, motivo = valid_campus_diferentes(horario, board, position, typeNum, INVALIDO)
    if result < 0: return result, motivo
    
    # Horário já está ocupado por outro no Quadro de horários?
    result, motivo = valid_horario_ocupado(horario, board, h_day, h_time, typeNum, position, subjectPos, INVALIDO, BREAK_INVALIDO)
    if result < 0: return result, motivo
    
    # Verificar também a parte dos professores
    result, motivo = valid_horario_ocupado_teachers(horario, board, h_day, h_time, typeNum, position, subjectPos, INVALIDO, BREAK_INVALIDO)
    if result < 0: return result, motivo

    # Não pode trabalhar mais de 8h no mesmo dia
    result, motivo = valid_menos_de_8h_dia(horario, position, INVALIDO)
    if result < 0: return result, motivo    

    # Não pode ter um intervalo entre uma aula e outra maior que 3h
    # Devem ser ao menos 11h entre o primeiro e o último horário de descanso
    # Status: aguardando reunião, atualmente seria impossível o estado acima citado não ser válido
    return 0, 'Tudo certo :)'

def valid_campus_diferentes(horario, board, position, typeNum, INVALIDO):
    for value in board[position[0]][typeNum]:
        if value:
            if not(type(value) is list):
                # Value é um horário normal
                if horario.local != value.local:
                    return INVALIDO, f'CAMPUS DIFERENTES EM UM MESMO TURNO 1 ____{horario.local}______'
            elif len(position) == 3: # Se for bimestral
                #if (len(h) == 4 and horario.type[2] == '1') or (len(h) == 3 and '4,G' in horario.type) or (len(h) == 2 and not('4,G' in horario.type or horario.type[2] == '1')):
                try:
                    tipo_diferente = False
                    for bimestral in value:
                        if bimestral:
                            if bimestral.type == horario.type:
                                break
                            else:
                                tipo_diferente = True
                                break
                    if tipo_diferente: 
                        raise Exception('é de tipo diferente')
                            
                    if value[position[2]]:
                        if value[position[2]].local != horario.local:
                            return INVALIDO, f'CAMPUS DIFERENTES EM UM MESMO TURNO 2 ___{horario.local}_______'
                except: # Vai passar por aqui quando as listas forem de comprimentos diferentes.
                    for bimestral in value:
                        if bimestral:
                            if bimestral.local != horario.local: 
                                #print(f'Erro, dia:{position[0]} listas diferentes')
                                return INVALIDO, f'CAMPUS DIFERENTES EM UM MESMO TURNO 3 ___{horario.local}_______'
            else: # Horario é do tipo normal e Value é bimestral
                for bimestral in value:
                    if bimestral:
                        if bimestral.local != horario.local: 
                            return INVALIDO, f'CAMPUS DIFERENTES EM UM MESMO TURNO 4 ___{horario.local}_______'
    return 0, ''

def valid_horario_ocupado(horario, board, h_day, h_time, typeNum, position, subjectPos, INVALIDO, BREAK_INVALIDO):
    if board[str(h_day)][typeNum][h_time] != 0: # Se horário estiver preenchido 
        if type(board[str(h_day)][typeNum][h_time]) is list and horario.teacher.bimestral[subjectPos] == 1: # Se horário preenchido for lista e o horário for bimestral
    
            # Temos essa situação especial, em que por mais que sejam listas diferentes, ainda podemos colocar os horários juntos.
            
            special_case = False
            if len(board[str(h_day)][typeNum][h_time]) == 4:
                if horario.type[2] == '2' and board[str(h_day)][typeNum][h_time].count(0):
                    if not(board[str(h_day)][typeNum][h_time][0]):
                        if not(board[str(h_day)][typeNum][h_time][1]):             special_case = True
                        elif board[str(h_day)][typeNum][h_time][1].type[2] == '2': special_case = True
                    elif board[str(h_day)][typeNum][h_time][0].type[2] == '2':
                        if not( board[str(h_day)][typeNum][h_time][1]):            special_case = True
                        elif board[str(h_day)][typeNum][h_time][1].type[2] == '2': special_case = True

                    if not(board[str(h_day)][typeNum][h_time][2]):
                        if not(board[str(h_day)][typeNum][h_time][3]):             special_case = True
                        elif board[str(h_day)][typeNum][h_time][3].type[2] == '2': special_case = True
                    elif board[str(h_day)][typeNum][h_time][2].type[2] == '2':
                        if not( board[str(h_day)][typeNum][h_time][3]):            special_case = True
                        elif board[str(h_day)][typeNum][h_time][3].type[2] == '2': special_case = True
            
            if ((horario.type[2] == '1' and len(board[str(h_day)][typeNum][h_time]) != 4) or (
                 '4,G' in horario.type and len(board[str(h_day)][typeNum][h_time]) != 3)) and (not(special_case)):
                return INVALIDO, f'HORÁRIO POSSUI TIPO DIFERENTE DOS DEMAIS _{horario.type}'
            if board[str(h_day)][typeNum][h_time][position[2]] != 0:
                return INVALIDO, 'HORÁRIO JÁ OCUPADO 2 _________'
            if not(special_case):
                for outros_horarios in board[str(h_day)][typeNum][h_time]:
                    if outros_horarios:
                        if outros_horarios.type != horario.type:
                            return INVALIDO, f'HORÁRIO POSSUI TIPO DIFERENTE DOS DEMAIS _{outros_horarios.type, horario.type}'
                        if outros_horarios.subject == horario.subject:
                            return INVALIDO, f'MESMA MATÉRIA FICA EM LISTAS DIFERENTES _{outros_horarios.subject, horario.subject}'
                        elif outros_horarios.teacher == horario.teacher:
                            return INVALIDO, f'MESMO PROFESSOR FICA EM LISTAS DIFERENTES_ '
            # Se horário estiver preenchido
            elif not(special_case):
                for outros_horarios in board[str(h_day)][typeNum][h_time]:
                    if outros_horarios:
                        # Se os outros horários da lista forem de tipos diferentes
                        if outros_horarios.type != horario.type or ('3,1,G' in horario.type and len(board[str(h_day)][typeNum][h_time]) != 4):
                            return INVALIDO, f'HORÁRIO POSSUI TIPO DIFERENTE DOS DEMAIS _{outros_horarios.type, horario.type}'
            try:        
                if board[str(h_day)][typeNum][h_time][position[2]] != 0:
                    return INVALIDO, 'HORÁRIO JÁ OCUPADO 2 _________'
            except:
                raise Exception(f'Erro no validation {board[str(h_day)][typeNum][h_time]}, {position[2]}')

        else: 
            return BREAK_INVALIDO, f'HORÁRIO JÁ OCUPADO 3 _tem um normal no lugar: {horario.type}'
    
    return 0, ''
    
def valid_horario_ocupado_teachers(horario, board, h_day, h_time, typeNum, position, subjectPos, INVALIDO, BREAK_INVALIDO):
    if type(horario.teacher.schedule[str(h_day)][typeNum]) is int:
        raise Exception('Horário no professor aparece com 0', horario, horario.teacher.schedule, horario.teacher.schedule[str(h_day)])
    
    special_case = False
    if type(board[str(h_day)][typeNum][h_time]) is list and horario.teacher.bimestral[subjectPos] == 1:
        if len(board[str(h_day)][typeNum][h_time]) == 4:
            if horario.type[2] == '2' and board[str(h_day)][typeNum][h_time].count(0):
                if not(board[str(h_day)][typeNum][h_time][0]):
                    if not(board[str(h_day)][typeNum][h_time][1]):             special_case = True
                    elif board[str(h_day)][typeNum][h_time][1].type[2] == '2': special_case = True
                elif board[str(h_day)][typeNum][h_time][0].type[2] == '2':
                    if not( board[str(h_day)][typeNum][h_time][1]):            special_case = True
                    elif board[str(h_day)][typeNum][h_time][1].type[2] == '2': special_case = True

                if not(board[str(h_day)][typeNum][h_time][2]):
                    if not(board[str(h_day)][typeNum][h_time][3]):             special_case = True
                    elif board[str(h_day)][typeNum][h_time][3].type[2] == '2': special_case = True
                elif board[str(h_day)][typeNum][h_time][2].type[2] == '2':
                    if not( board[str(h_day)][typeNum][h_time][3]):            special_case = True
                    elif board[str(h_day)][typeNum][h_time][3].type[2] == '2': special_case = True

    if horario.teacher.schedule[str(h_day)][typeNum][h_time] != 0: # Se horário preenchido 
        if type(horario.teacher.schedule[str(h_day)][typeNum][h_time]) is list and horario.teacher.bimestral[subjectPos] == 1: # Se horário preenchido for lista e o horário for bimestral
            
            
            if not(0 in horario.teacher.schedule[str(h_day)][typeNum][h_time]):
                return BREAK_INVALIDO, 'HORÁRIO JA PREENCHIDO PROFESSORES 1 _______'
            
            
            for bimestral in horario.teacher.schedule[str(h_day)][typeNum][h_time]:
                if bimestral:
                    if '1' != horario.type[0]:
                        return INVALIDO, 'Não pode ter mais de uma posição PREENCHIDA'
            

            # Se horário estiver preenchido
                #Precisamos antes checar se as condições do horário estão corretas, se é compatível o horário que estamos colocando com o local em que ele será colocado
            if (not special_case) and ((len(horario.teacher.schedule[str(h_day)][typeNum][h_time]) == 4 and '1' == horario.type[2]) or (len(horario.teacher.schedule[str(h_day)][typeNum][h_time]) == 2 and '2,T' in horario.type) or (len(horario.teacher.schedule[str(h_day)][typeNum][h_time]) == 3 and '4,G' in horario.type)):
                try: 
                    if horario.teacher.schedule[str(h_day)][typeNum][h_time][position[2]] != 0:
                        return INVALIDO, 'HORÁRIO JA PREENCHIDO PROFESSORES 2 _______'
                except:
                    print('Posição e horário não estão de acordo', position[2], horario.type)
                    if horario.teacher.schedule[str(h_day)][typeNum][h_time][position[2]] != 0:
                        pass
            elif not special_case:
                return INVALIDO, 'TIPO DO PROFESSOR E DO HORÁRIO NÃO CORRESPONDEM ______'
            
        else: 
            return BREAK_INVALIDO, 'HORÁRIO JA PREENCHIDO PROFESSORES 3 _______'
    
    if horario.coteacher:
        if horario.teacher.schedule[str(h_day)][typeNum][h_time] != 0: # Se horário preenchido 
            if type(horario.coteacher.schedule[str(h_day)][typeNum][h_time]) is list and not('0' in horario.type): # Se horário preenchido for lista e o horário for bimestral
                
                
                if not(0 in horario.coteacher.schedule[str(h_day)][typeNum][h_time]):
                    return BREAK_INVALIDO, 'HORÁRIO JA PREENCHIDO PROFESSORES 1 _______'
                
                
                for bimestral in horario.coteacher.schedule[str(h_day)][typeNum][h_time]:
                    if bimestral:
                        if '1' != horario.type[0]:
                            return INVALIDO, 'Não pode ter mais de uma posição PREENCHIDA'
                

                # Se horário estiver preenchido
                    #Precisamos antes checar se as condições do horário estão corretas, se é compatível o horário que estamos colocando com o local em que ele será colocado
                if (not special_case) and ((len(horario.coteacher.schedule[str(h_day)][typeNum][h_time]) == 4 and '1' == horario.type[2]) or (len(horario.coteacher.schedule[str(h_day)][typeNum][h_time]) == 2 and '2,T' in horario.type) or (len(horario.coteacher.schedule[str(h_day)][typeNum][h_time]) == 3 and '4,G' in horario.type)):
                    try: 
                        if horario.coteacher.schedule[str(h_day)][typeNum][h_time][position[2]] != 0:
                            return INVALIDO, 'HORÁRIO JA PREENCHIDO PROFESSORES 2 _______'
                    except:
                        print('Posição e horário não estão de acordo', position[2], horario.type)
                        if horario.coteacher.schedule[str(h_day)][typeNum][h_time][position[2]] != 0:
                            pass
                elif not special_case:
                    return INVALIDO, 'TIPO DO PROFESSOR E DO HORÁRIO NÃO CORRESPONDEM ______'
                
            else: 
                return BREAK_INVALIDO, 'HORÁRIO JA PREENCHIDO PROFESSORES 3 _______'
    
    return 0, ''

def valid_menos_de_8h_dia(horario, position, INVALIDO):
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
    return 0, ''

def valid_limitations(horario, h_day, h_time, typeNum, subjectPos, INVALIDO):
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
    return 0, ''




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
    Se o horário for bimestral e não tiver uma lista na posição de destino, criamos a lista
    Trocamos tanto o horário dos professores deposição quanto os do quadro
    """
    #if type(quadro[turma][d2][turno][p2]) is list:
        #if h1.type[2] == '2' and len(quadro[turma][d2][turno][p2]) == 4:
            #replace_special_case()
    print('r', end='')
    
    if pb_1 != 'Nada':
        
        if type(quadro[turma][d1][turno][p1]) is list:
            quadro[turma][d1][turno][p1][pb_1] = h2
        else:
            if '1' == h2.type[2]:
                if not(quadro[turma][d1][turno][p1]): 
                    print(f' C ', end='')
                    quadro[turma][d1][turno][p1] = [0, 0, 0, 0]
            elif '4,G' in h2.type:
                if not(quadro[turma][d1][turno][p1]): 
                    print(f' C ', end='')
                    quadro[turma][d1][turno][p1] = [0, 0, 0]
            else:
                if not(quadro[turma][d1][turno][p1]): 
                    print(f' C ', end='')
                    quadro[turma][d1][turno][p1] = [0, 0]
            # Colocamos o horário na posição
            quadro[turma][d1][turno][p1][pb_1] = h2

        if type(quadro[turma][d2][turno][p2]) is list:
            quadro[turma][d2][turno][p2][pb_2] = h1
        else:
            if '1' == h1.type[2]:
                if not(quadro[turma][d2][turno][p2]): 
                    quadro[turma][d2][turno][p2] = [0, 0, 0, 0]
                    print(f' C ', end='')
            elif '4,G' in h1.type:
                if not(quadro[turma][d2][turno][p2]): 
                    quadro[turma][d2][turno][p2] = [0, 0, 0]
                    print(f' C ', end='')
            else:
                if not(quadro[turma][d2][turno][p2]): 
                    quadro[turma][d2][turno][p2] = [0, 0]
                    print(f' C ', end='')
            # Colocamos o horário na posição
            try: quadro[turma][d2][turno][p2][pb_2] = h1
            except:
                print(len(quadro[turma][d2][turno][p2]), h1.type, )
                raise Exception(f'Erro no replace_h {len(quadro[turma][d2][turno][p2])}, h1-{h1.type}, h2-{h2}, {pb_2}')
        
        if type(h1.teacher.schedule[d2][turno][p2]) is list:
            try: h1.teacher.schedule[d2][turno][p2][pb_2] = f"{h1.turm[0]}-{str(h1).split('-')[1]}"
            except:
                raise Exception(f'Erro no replace_h, professor: {len(h1.teacher.schedule[d2][turno][p2])}, h1-{h1.type}, h2-{h2}, {pb_2}')
            #print('colocando h1 com lista')
        else:
            if '1' == h1.type[2]:
                if not(h1.teacher.schedule[d2][turno][p2]): h1.teacher.schedule[d2][turno][p2] = [0, 0, 0, 0]
                else: print('H1 --->',  h1.teacher.schedule[d2][turno][p2])
            elif '4,G' in h1.type:
                if not(h1.teacher.schedule[d2][turno][p2]): h1.teacher.schedule[d2][turno][p2] = [0, 0, 0]
                else: print('H1 --->',  h1.teacher.schedule[d2][turno][p2])
            else:
                if not(h1.teacher.schedule[d2][turno][p2]): h1.teacher.schedule[d2][turno][p2] = [0, 0]
                else: print('H1 --->',  h1.teacher.schedule[d2][turno][p2])

            h1.teacher.schedule[d2][turno][p2][pb_2] = f"{h1.turm[0]}-{str(h1).split('-')[1]}"
        if h2: # Se h2 não for 0
            if type(h2.teacher.schedule[d1][turno][p1]) is list:
                h2.teacher.schedule[d1][turno][p1][pb_1] = f"{h2.turm[0]}-{str(h2).split('-')[1]}"
            else:
                if '1' == h2.type[2]:
                    if not(h2.teacher.schedule[d1][turno][p1]): h2.teacher.schedule[d1][turno][p1] = [0, 0, 0, 0]
                    else: print('H2 --->', h2.teacher.schedule[d1][turno][p1])
                elif '4,G' in h2.type:
                    if not(h2.teacher.schedule[d1][turno][p1]): h2.teacher.schedule[d1][turno][p1] = [0, 0, 0]
                    else: print('H2 --->', h2.teacher.schedule[d1][turno][p1])
                else:
                    if not(h2.teacher.schedule[d1][turno][p1]): h2.teacher.schedule[d1][turno][p1] = [0, 0]
                    else: print('H2 --->', h2.teacher.schedule[d1][turno][p1])
                try: h2.teacher.schedule[d1][turno][p1][pb_1] = f"{h2.turm[0]}-{str(h2).split('-')[1]}"
                except:
                    print('É isso que estamos tentando fazer: ', h2.type, h2.type[2], h2.teacher.schedule[d1][turno][p1], pb_1)
                    h2.teacher.schedule[d1][turno][p1][pb_1] = f"{h2.turm[0]}-{str(h2).split('-')[1]}"

        
    else: # Ambos os horários são normais
        print('Normal', end='')
        quadro[turma][d1][turno][p1] = h2
        quadro[turma][d2][turno][p2] = h1
        h1.teacher.schedule[d2][turno][p2] = f"{h1.turm[0]}-{str(h1).split('-')[1]}"
        if h2: h2.teacher.schedule[d1][turno][p1] = f"{h2.turm[0]}-{str(h2).split('-')[1]}"
        else: pass   # Pode acontecer caso h2 seja 0
    
def replace_special_case(quadro, turma, turno, h1, d1, p1, h2, d2, p2, positions_for_horaries, pb_1='Nada', pb_2='Nada'):
    print('ESPECIAL')
    if h2 == 0:
        if len(quadro[turma][d1][turno][p1]) == 4 and quadro[turma][d1][turno][p1].count(0) < 2:
            raise Exception('Invalido para ser caso especial')
        # Colocar na posição que estava o h1 o h2
        if pb_1 > 1:
            quadro[turma][d1][turno][p1][2] = h2
            quadro[turma][d1][turno][p1][3] = h2
            
        else:
            quadro[turma][d1][turno][p1][0] = h2
            quadro[turma][d1][turno][p1][1] = h2

        # Colocar na posição que estava o h2 o h1
        quadro[turma][d2][turno][p2][pb_2] = h1
        h1.teacher.schedule[d2][turno][p2][pb_2] = h1
        
    else: # Vale a pena manter essa possibilidade?
        if len(quadro[turma][d1][turno][p1]) == 4 and h2.type[2] == '2':
            if quadro[turma][d1][turno][p1].count(0) < 2:
                raise Exception('Invalido para ser caso especial')
            if pb_1 > 1:
                quadro[turma][d1][turno][p1][2] = h2
                quadro[turma][d1][turno][p1][3] = h2
                h2.teacher.schedule[d1][turno][p1][2] = h2
                h2.teacher.schedule[d1][turno][p1][3] = h2  
                if len(quadro[turma][d2][turno][p2]) == 4 and h1.type[2] == '2':
                    # Estamos trocando dois horários especiais de posição
                    if pb_2 > 1:
                        quadro[turma][d2][turno][p2][2] = h1
                        quadro[turma][d2][turno][p2][3] = h1
                        h1.teacher.schedule[d1][turno][p1][2] = h1
                        h1.teacher.schedule[d1][turno][p1][3] = h1
                    else:
                        quadro[turma][d2][turno][p2][0] = h1
                        quadro[turma][d2][turno][p2][1] = h1
                        h1.teacher.schedule[d1][turno][p1][0] = h1
                        h1.teacher.schedule[d1][turno][p1][1] = h1
                else:
                    # Estamos trocando um normal com um especial de posição.
                    # Será [X, X, S, S] -> [X, ]
                    quadro[turma][d2][turno][p2][pb_2] = h1
                    h1.teacher.schedule[d2][turno][p2][pb_2] = h1
                    
                    
            else:
                quadro[turma][d1][turno][p1][0] = h2
                quadro[turma][d1][turno][p1][1] = h2
                h2.teacher.schedule[d1][turno][p1][0] = h2
                h2.teacher.schedule[d1][turno][p1][1] = h2
                if len(quadro[turma][d2][turno][p2]) == 4 and h1.type[2] == '2':
                    # Estamos trocando dois horários especiais de posição
                    if pb_2 > 1:
                        quadro[turma][d2][turno][p2][2] = h1
                        quadro[turma][d2][turno][p2][3] = h1
                        h1.teacher.schedule[d1][turno][p1][2] = h1
                        h1.teacher.schedule[d1][turno][p1][3] = h1
                    else:
                        quadro[turma][d2][turno][p2][0] = h1
                        quadro[turma][d2][turno][p2][1] = h1
                        h1.teacher.schedule[d1][turno][p1][0] = h1
                        h1.teacher.schedule[d1][turno][p1][1] = h1
                else:
                    # Estamos trocando um semestral com um especial de posição
                    quadro[turma][d2][turno][p2][pb_2] = h1
                    h1.teacher.schedule[d2][turno][p2][pb_2] = h1

        elif len(quadro[turma][d2][turno][p2]) == 4 and h1.type[2] == '2':
            if quadro[turma][d2][turno][p2].count(0) < 2:
                raise Exception('Invalido para ser caso especial')
            pass
        else:
            raise Exception('Não é compátivel com nenhum dos casos especiais.')

def print_quadro(quadro, horario, typeNum):
    print(f'========== PROFESSOR {horario.teacher}')
    try: h = quadro[horario.turm[0]]
    except: 
        raise Exception(f'Erro com o quadro no print: {horario.turm[0]}, {quadro.keys()}')
    for variavel in horario.teacher.schedule.values():
        print(len(variavel), end=' ')
        print('[', end='')
        for value in variavel[typeNum]:
            if value:
                if type(value) is list:
                    print('[', end='')
                    for bimestre in value:
                        if bimestre: 
                            print('X', end=', ')
                        else: print(' ', end=', ')
                    print(']', end=', ')
                else:
                    print('X', end=', ')
                
            else: print(' ', end=', ')
        print(' ]')
    if horario.coteacher:
        print('========== COTEACHER')
        for variavel in horario.coteacher.schedule.values():
            print(len(variavel), end=' ')
            print('[', end='')
            for value in variavel[typeNum]:
                if value:
                    if type(value) is list:
                        print('[', end='')
                        for bimestre in value:
                            if bimestre: 
                                print('X', end=', ')
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
                        if bimestre: 
                            if '1' in bimestre.local:
                                print(f'{bimestre.type[2]}', end=', ')
                            else:
                                print(f'{bimestre.type[2]}', end=', ')
                        else: print(' ', end=', ')
                    print(']', end=', ')
                else:
                    if '1' in value.local:
                        print(f'{value.type[2]}', end=', ')
                    else:
                        print(f'{value.type[2]}', end=', ')
                
            else: print(' ', end=', ')
        print(' ]')

def days_with_zero(quadro, turno, turma):
    """
    Vamos criar uma lista com apenas os dias que possuem 0, e vamos fazer com que o programa dê preferência para eles
    """
    result = []
    for dia, horarios in quadro[turma].items():
        for horario in horarios[turno]:
            if horario == 0:
                result.append(dia)
            elif type(horario) is list:
                for bimestral in horario:
                    if not(bimestral):
                        result.append(dia)
                        break
    return result



def generate_list_position(quadro, turno, turma, just_zeros=True):
    """
    Vamos criar uma lista com todos os possíveis conjuntos de valores que h1 e h2 podem ter
    h1 não pode ser 0
    h2 tem que ser do mesmo tipo que h1
    """
    #print(just_zeros, end=' ')
    #print(' ')
    #print('generating list...', end='')
    result = []
    for dia_1 in range(2, 7):
        dia_1 = str(dia_1)
        if quadro[turma][dia_1][turno].count(0) == len(quadro[turma][dia_1][turno]) and just_zeros:
            continue
        for p1 in range(0, len(quadro[turma][dia_1][turno])):
            if quadro[turma][dia_1][turno][p1] == 0:
                continue
            elif type(quadro[turma][dia_1][turno][p1]) is list:
                # Se acharmos um pb_1 que não é 0, temos que então achar um pb_2
                for pb1 in range(0, len(quadro[turma][dia_1][turno][p1])):
                    if quadro[turma][dia_1][turno][p1][pb1] == 0:
                        continue
                    """
                    elif not(str(quadro[turma][dia_1][turno][p1][pb1].teacher.schedule[dia_1][turno][p1][pb1]).split('-')[-1] in str(quadro[turma][dia_1][turno][p1][pb1])):
                        print('No Generating teacher != Quadro, BIMESTRAL1')
                        raise Exception(f'Está diferente ({dia_1, p1, pb1})')
                    """

                    for dia_2 in range(2, 7):
                        dia_2 = str(dia_2)
                        for p2 in range(0, len(quadro[turma][dia_1][turno])):
                            if type(quadro[turma][dia_2][turno][p2]) is list:
                                if len(quadro[turma][dia_2][turno][p2]) == len(quadro[turma][dia_1][turno][p1]):
                                    
                                    invalido = False
                                    for bimestral in quadro[turma][dia_2][turno][p2]:
                                        if bimestral:
                                            if bimestral.teacher == quadro[turma][dia_1][turno][p1][pb1].teacher:
                                                invalido = True
                                                break
                                    if not(invalido):
                                            
                                        for pb2 in range(0, len(quadro[turma][dia_2][turno][p2])):
                                            if not(quadro[turma][dia_2][turno][p2][pb2]):
                                                if valid_positions(quadro, turma, turno, (dia_1, p1, pb1, dia_2, p2, pb2), result):
                                                    result.append((dia_1, p1, pb1, dia_2, p2, pb2))
                                                    
                                                else: continue
                                                
                                            if not(just_zeros) and quadro[turma][dia_2][turno][p2][pb2]:
                                                if quadro[turma][dia_2][turno][p2][pb2].type != quadro[turma][dia_1][turno][p1][pb1].type:
                                                    break
                                                elif quadro[turma][dia_2][turno][p2][pb2] == quadro[turma][dia_1][turno][p1][pb1]:
                                                    pass
                                                else:
                                                    if valid_positions(quadro, turma, turno, (dia_1, p1, pb1, dia_2, p2, pb2), result):
                                                        result.append((dia_1, p1, pb1, dia_2, p2, pb2))
                                                    else: continue
                                                    
                                            else:
                                                pass
                                                #print(quadro[turma][dia_2][turno][p2][pb2], end=' ')
                                elif len(quadro[turma][dia_2][turno][p2]) == 4 and quadro[turma][dia_1][turno][p1][pb1].type[2] == '2': # Temos um caso especial:
                                    pb2 = random.randint(0, len(quadro[turma][dia_1][turno][p1])-1)
                                    if valid_positions(quadro, turma, turno, (dia_1, p1, pb1, dia_2, p2, pb2), result):
                                        result.append((dia_1, p1, pb1, dia_2, p2, pb2))
                            elif not(quadro[turma][dia_2][turno][p2]): # Caso selecionemos um horário vazio que nem tenha uma lista nele.
                                pb2 = random.randint(0, len(quadro[turma][dia_1][turno][p1])-1)
                                if valid_positions(quadro, turma, turno, (dia_1, p1, pb1, dia_2, p2, pb2), result):
                                    result.append((dia_1, p1, pb1, dia_2, p2, pb2))
                                    
                                else: continue
                                if quadro[turma][dia_1][turno][p1][pb1] == 0:
                                    print('Estamos adicionando um h1 == 0')
            else: # Se h1 for normal, temos que selecionar um h2 normal
                if not(str(quadro[turma][dia_1][turno][p1].teacher.schedule[dia_1][turno][p1]).split('-')[-1] in str(quadro[turma][dia_1][turno][p1])):
                    print('No Generating teacher != Quadro, NORMAL')
                    raise Exception(f'Está diferente {dia_1, p1}')
                for dia_2 in range(2, 7):
                    dia_2 = str(dia_2)
                    for p2 in range(0, len(quadro[turma][dia_1][turno])):
                        
                        if not(type(quadro[turma][dia_2][turno][p2]) is list):
                            if not(quadro[turma][dia_2][turno][p2]):
                                if valid_positions(quadro, turma, turno, (dia_1, p1, dia_2, p2), result):
                                    result.append((dia_1, p1, dia_2, p2))
                            elif not(just_zeros):
                                if valid_positions(quadro, turma, turno, (dia_1, p1, dia_2, p2), result):
                                    result.append((dia_1, p1, dia_2, p2))
                                if quadro[turma][dia_1][turno][p1] == 0:
                                    print('Estamos adicionando um h1 == 0, normal')
                            else:
                                pass
    
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
    #print('a', end='')
    """
    if type(quadro[turma][d2][turno][p2]) is list:
        if quadro[turma][d2][turno][p2][pb2].teacher.schedule[d2][turno][p2].count(0) == len(quadro[turma][d2][turno][p2][pb2].teacher.schedule[d2][turno][p2]):
            quadro[turma][d2][turno][p2][pb2].teacher.schedule[d2][turno][p2] = 0
        try:
            if quadro[turma][d1][turno][p1][pb1].teacher.schedule[d1][turno][p1].count(0) == len(quadro[turma][d1][turno][p1][pb1].teacher.schedule[d1][turno][p1]):
                quadro[turma][d1][turno][p1][pb1].teacher.schedule[d1][turno][p1] = 0
        except: pass
    """

    valores_a_serem_acrescentados = []
    valores_a_serem_removidos = []
    #print(f'TROCADO <<{d1, p1}, {d2, p2}>>')
        
    for valor in lista:
        if len(valor) == 4 and pb1 == None:
            if (type(quadro[turma][valor[0]][turno][valor[1]]) is list) or (type(quadro[turma][valor[2]][turno][valor[3]])):
                valores_a_serem_removidos.append(valor)
                continue
            if (valor[0] == d1) and (valor[1] == p1): # Achamos um:
                if valid_positions(quadro, turma, turno, (d2, p2, valor[2], valor[3]), lista):
                    valores_a_serem_acrescentados.append((d2, p2, valor[2], valor[3]))
                else: valores_a_serem_removidos.append((d2, p2, valor[2], valor[3]))
                valores_a_serem_removidos.append(valor)
            elif(valor[2] == d1) and (valor[3] == p1):
                if valid_positions(quadro, turma, turno, (valor[0], valor[1], d2, p2), lista):
                    valores_a_serem_acrescentados.append((valor[0], valor[1], d2, p2))
                else: valores_a_serem_removidos.append((valor[0], valor[1], d2, p2))
                valores_a_serem_removidos.append(valor)
            if (valor[0] == d2) and (valor[1] == p2): # Achamos um:
                if valid_positions(quadro, turma, turno, (d1, p1, valor[2], valor[3]), lista):
                    valores_a_serem_acrescentados.append((d1, p1, valor[2], valor[3]))
                else: valores_a_serem_removidos.append((d1, p1, valor[2], valor[3]))
                valores_a_serem_removidos.append(valor)
            elif(valor[2] == d2) and (valor[3] == p2):
                if valid_positions(quadro, turma, turno, (valor[0], valor[1], d1, p1), lista):
                    valores_a_serem_acrescentados.append((valor[0], valor[1], d1, p1))
                else: valores_a_serem_removidos.append((valor[0], valor[1], d1, p1))
                valores_a_serem_removidos.append(valor)
        elif len(valor) == 6 and pb1 != None:
            if (type(quadro[turma][valor[0]][turno][valor[1]]) is classes.Horario) or (type(quadro[turma][valor[3]][turno][valor[4]]) is classes.Horario):
                valores_a_serem_removidos.append(valor)
                continue
            # Se tivermos alguma posição com uma lista vazia, transformamos ela em apenas 0 para podermos colocar qualquer horário ali.
            
            if type(quadro[turma][valor[3]][turno][valor[4]]) is list:
                pass
                # Vamos ver se não temos listas vazias na grade horária
                position_to_change = zero_list(quadro, turma, turno, lista, valor)
                #valores_a_serem_acrescentados += position_to_change[0]
                valores_a_serem_removidos += position_to_change[1]
            
            if (valor[0] == d1) and (valor[1] == p1) and (valor[2] == pb1):
                if valid_positions(quadro, turma, turno, (d2, p2, pb2, valor[3], valor[4], valor[5]), lista):
                    valores_a_serem_acrescentados.append((d2, p2, pb2, valor[3], valor[4], valor[5]))
                else: valores_a_serem_removidos.append((d2, p2, pb2, valor[3], valor[4], valor[5]))
                valores_a_serem_removidos.append(valor)
            elif (valor[3] == d1) and (valor[4] == p1) and (valor[5] == pb1):
                if valid_positions(quadro, turma, turno, (valor[0], valor[1], valor[2], d2, p2, pb2), lista):
                    valores_a_serem_acrescentados.append((valor[0], valor[1], valor[2], d2, p2, pb2))
                else: valores_a_serem_removidos.append((valor[0], valor[1], valor[2], d2, p2, pb2))
                valores_a_serem_removidos.append(valor)

            elif (valor[0] == d2) and (valor[1] == p2) and (valor[2] == pb2):
                if valid_positions(quadro, turma, turno, (d1, p1, pb1, valor[3], valor[4], valor[5]), lista):
                    valores_a_serem_acrescentados.append((d1, p1, pb1, valor[3], valor[4], valor[5]))
                else: valores_a_serem_removidos.append((d1, p1, pb1, valor[3], valor[4], valor[5]))
                valores_a_serem_removidos.append(valor)
            elif (valor[3] == d2) and (valor[4] == p2) and (valor[5] == pb2):
                if valid_positions(quadro, turma, turno, (valor[0], valor[1], valor[2], d1, p1, pb1), lista):
                    valores_a_serem_acrescentados.append((valor[0], valor[1], valor[2], d1, p1, pb1))
                else: valores_a_serem_removidos.append((valor[0], valor[1], valor[2], d1, p1, pb1))
                valores_a_serem_removidos.append(valor)
        elif len(valor) == 4:
            # Temos esse if apenas porsegurança
            if type(quadro[turma][valor[2]][turno][valor[3]]) is list:
                valores_a_serem_removidos.append(valor)
        if not (valor in valores_a_serem_removidos):
            if not(valid_positions(quadro, turma, turno, valor, lista)):
                valores_a_serem_removidos.append(valor)
    # Removemos os valores do resultado.
    for valor in valores_a_serem_removidos:
        while valor in lista:
            lista.remove(valor)
        while valor in valores_a_serem_acrescentados: 
            valores_a_serem_acrescentados.remove(valor)
    
    for p in lista:
        if not(valid_positions(quadro, turma, turno, p, lista)):
            raise Exception(f'{p}, {d1, p1, pb1, d2, p2, pb2} Erro no final do actualize')
    
    return lista  + valores_a_serem_acrescentados

def actualize(teachers, new_teachers):
    """
    Vamos pegar os valores dos objetos que estamos usando e atualizá-los em função dos objetos que encontramos
    """
    #print('actualize...')
    for old in teachers:
        for new in new_teachers:
            if old.name == new.name:
                if old.schedule != new.schedule:
                    #print('|', end='')
                    old.schedule = copy.deepcopy(new.schedule)
                    break

def valid_positions(quadro, turma, turno, p, lista):
    """
    Dadas duas posições da lista dos horários, vamos ver se elas são válidas.
    Vamos usar para checar se está tudo certo a lista de posições que estamos gerando.
    """
    
    if len(p) == 6:
        if quadro[turma][p[0]][turno][p[1]]: # Se a primeira posição for 0, removemos ela da lista
            if quadro[turma][p[0]][turno][p[1]][p[2]] == 0:
                #print(f'o', end='')
                return False
        if quadro[turma][p[3]][turno][p[4]]:
            if type(quadro[turma][p[0]][turno][p[1]]) != type(quadro[turma][p[3]][turno][p[4]]):
                #print('d', end='')
                return False
        if quadro[turma][p[3]][turno][p[4]]: # Vamos ver se o quadro está igual ao do professor
            if len(quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]]) != len(quadro[turma][p[3]][turno][p[4]]):
                #print('L', end='')
                return False
        if (p[0] == p[3]) and (p[1] == p[4]) and (p[2] == p[5]): # Vamos ver se não temos nada duplicado
            return False
        if (p[3], p[4], p[5], p[0], p[1], p[2]) in lista: # Vamos ver se não tem as mesmas posições na lista, sóque no lugar de ser 1 -> 2 é 2 -> 1
            #print('&', end='')
            return False
        
        if type(quadro[turma][p[0]][turno][p[1]]) is list:
            if type(quadro[turma][p[3]][turno][p[4]]) is list:
                if (len(quadro[turma][p[3]][turno][p[4]]) != len(quadro[turma][p[0]][turno][p[1]])) or len(quadro[turma][p[3]][turno][p[4]]) <= p[5]:
                    #print('~', end='')
                    return False
                if quadro[turma][p[3]][turno][p[4]][p[5]]:
                    if quadro[turma][p[0]][turno][p[1]][p[2]].type != quadro[turma][p[3]][turno][p[4]][p[5]].type:
                        if not((quadro[turma][p[0]][turno][p[1]][p[2]].type[2] == '2') and (len(quadro[turma][p[3]][turno][p[4]][p[5]]) == 4) and (quadro[turma][p[0]][turno][p[1]][p[2]].count(0) != 2)): # Caso especial    
                            #print('0', end='')
                            return False
                if len(quadro[turma][p[0]][turno][p[1]]) != len(quadro[turma][p[3]][turno][p[4]]):
                    #print('0', end='')
                    return False
                if not(str(quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]]).split('-')[-1] in str(quadro[turma][p[0]][turno][p[1]][p[2]])):
                    #print('O', end='')
                    raise Exception('Professor diferente do Quadro')
                    
                if quadro[turma][p[3]][turno][p[4]]:
                    if quadro[turma][p[3]][turno][p[4]][p[5]]:
                        if not(str(quadro[turma][p[3]][turno][p[4]][p[5]].teacher.schedule[p[3]][turno][p[4]][p[5]]).split('-')[-1] in str(quadro[turma][p[3]][turno][p[4]][p[5]])):
                            #print('O', end='')
                            raise Exception('Professor diferente do Quadro')
            elif not(type(quadro[turma][p[3]][turno][p[4]]) is int):
                #print('0', end='')
                return False
            else:
                if p[5] >= len(quadro[turma][p[0]][turno][p[1]]):
                    #print('L', end='')
                    return False
        else: 
            #print('0', end='')
            return False
        if quadro[turma][p[3]][turno][p[4]]:
            if '1' == quadro[turma][p[0]][turno][p[1]][p[2]].type[2]:
                if len(quadro[turma][p[3]][turno][p[4]]) != 4: 
                    #print('L! ', end='')
                    return False
            elif '4,G' in quadro[turma][p[0]][turno][p[1]][p[2]].type:
                if len(quadro[turma][p[3]][turno][p[4]]) != 3: 
                    #print('L! ', end='')
                    return False
            else:
                if len(quadro[turma][p[3]][turno][p[4]]) != 2: 
                    #print('L! ', end='')
                    return False
               
    else: # No caso do horário ser normal
        if (p[2], p[3], p[0], p[1]) in lista:
            #print('&', end='')
            return False
        if (p[0] == p[2]) and (p[1] == p[3]):
            return False
        if not(quadro[turma][p[0]][turno][p[1]]):
            #print(f'o{p} ', end='')
            return False
        if type(quadro[turma][p[0]][turno][p[1]]) is list or type(quadro[turma][p[0]][turno][p[1]]) is int:
            #print('0', end='')
            return False
        elif type(quadro[turma][p[2]][turno][p[3]]) is list:
            #print('0', end='')
            return False
        elif not(str(quadro[turma][p[0]][turno][p[1]].teacher.schedule[p[0]][turno][p[1]]).split('-')[-1] in str(quadro[turma][p[0]][turno][p[1]])):
            #print('O', end='')
            raise Exception('Professor diferente do Quadro')
        if quadro[turma][p[2]][turno][p[3]]:
            if not(str(quadro[turma][p[0]][turno][p[1]].teacher.schedule[p[0]][turno][p[1]]).split('-')[-1] in str(quadro[turma][p[0]][turno][p[1]])):
                #print(f'O', end='')
                raise Exception('Professor diferente do Quadro')
    return True



def zero_list(quadro, turma, turno, position_for_horaries, valor):
    """
    Quando tivermos uma lista, ou no quadro ou no professor, cujo todos os valore sejam 0, vamos remover a lista e colocar um 0 no lugar.
    Dessa forma, vamos poder colocar qualquer tipo de horário lá.
    """
    """
    for p in position_for_horaries:
        if len(p) == 6:
            if quadro[turma][p[0]][turno][p[1]][p[2]]:
                if not(str(quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]]).split('-')[-1] in str(quadro[turma][p[0]][turno][p[1]][p[2]])):
                    print('START', quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]], quadro[turma][p[0]][turno][p[1]][p[2]])
                    break
            else:
                if quadro[turma][p[3]][turno][p[4]][p[5]]:
                    if not(str(quadro[turma][p[3]][turno][p[4]][p[5]].teacher.schedule[p[3]][turno][p[4]][p[5]]).split('-')[-1] in str(quadro[turma][p[3]][turno][p[4]][p[5]])):
                        print('START', quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]], quadro[turma][p[0]][turno][p[1]][p[2]])
                        break
        else:
            if not(str(quadro[turma][p[0]][turno][p[1]].teacher.schedule[p[0]][turno][p[1]]).split('-')[-1] in str(quadro[turma][p[0]][turno][p[1]])):
                print('START', quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]], quadro[turma][p[0]][turno][p[1]][p[2]])
                break
            else:
                if quadro[turma][p[2]][turno][p[3]]:
                    if not(str(quadro[turma][p[2]][turno][p[3]].teacher.schedule[p[2]][turno][p[3]]).split('-')[-1] in str(quadro[turma][p[2]][turno][p[3]])):
                        print('START', quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]], quadro[turma][p[0]][turno][p[1]][p[2]])
                        break
    """     
    valores_a_adicionar = []
    valores_a_remover = []
    if not(valid_positions(quadro, turma, turno, valor, position_for_horaries)):
        return [], [valor]
    if len(valor) == 6:
        if not(quadro[turma][valor[0]][turno][valor[1]][valor[2]]):
            if quadro[turma][valor[0]][turno][valor[1]].count(0) == len(quadro[turma][valor[0]][turno][valor[1]]):
                quadro[turma][valor[0]][turno][valor[1]] = 0
                print(f' Z ', end='') #({valor[0], valor[1]})
                #changes = h_to_be_changed(quadro, turma, turno, position_for_horaries, day, position)
                #valores_a_adicionar += changes[0]
                #valores_a_remover += changes[1]
        else:
            # Não precisamos nem adicionar nem remover nenhuma posição quando mudamos nos professores, essa informação só é importante no validation
            for day in quadro[turma][valor[0]][turno][valor[1]][valor[2]].teacher.schedule.keys():
                for position in range(0, len(quadro[turma][valor[0]][turno][valor[1]][valor[2]].teacher.schedule[day][turno])):
                    if type(quadro[turma][valor[0]][turno][valor[1]][valor[2]].teacher.schedule[day][turno][position]) is list:
                        if quadro[turma][valor[0]][turno][valor[1]][valor[2]].teacher.schedule[day][turno][position].count(0) == len(quadro[turma][valor[0]][turno][valor[1]][valor[2]].teacher.schedule[day][turno][position]):
                            quadro[turma][valor[0]][turno][valor[1]][valor[2]].teacher.schedule[day][turno][position] = 0
                            #print('Zt', end='')
                            
        if not(quadro[turma][valor[3]][turno][valor[4]][valor[5]]):
            if quadro[turma][valor[3]][turno][valor[4]].count(0) == len(quadro[turma][valor[3]][turno][valor[4]]):
                quadro[turma][valor[3]][turno][valor[4]] = 0
                print(f' Z ', end='') #({valor[3], valor[4]})
                
                #changes = h_to_be_changed(quadro, turma, turno, position_for_horaries, day, position)
                #valores_a_adicionar += changes[0]
                #valores_a_remover += changes[1]
        else:
            for day in quadro[turma][valor[3]][turno][valor[4]][valor[5]].teacher.schedule.keys():
                for position in range(0, len(quadro[turma][valor[3]][turno][valor[4]][valor[5]].teacher.schedule[day][turno])):
                    if type(quadro[turma][valor[3]][turno][valor[4]][valor[5]].teacher.schedule[day][turno][position]) is list:
                        if quadro[turma][valor[3]][turno][valor[4]][valor[5]].teacher.schedule[day][turno][position].count(0) == len(quadro[turma][valor[3]][turno][valor[4]][valor[5]].teacher.schedule[day][turno][position]):
                            quadro[turma][valor[3]][turno][valor[4]][valor[5]].teacher.schedule[day][turno][position] = 0
                            #print('Zt', end='')
                            
    return valores_a_adicionar, valores_a_remover

def h_to_be_changed(quadro, turma, turno, positions_for_horaries, day, position):
    """
    Após zeramos uma lista, vamos selecionar todas as posições que passam a ser viáveis bem como todas as que vão deixar de ser viáveis.
    Todos os horários não vagos são opções viáveis para adicionarmos
    """

    add = []
    remove = []
    for valor in positions_for_horaries:
        if len(valor) == 6:
            for c in range(0, len(quadro[turma][valor[0]][turno])):
                if valid_positions(quadro, turma, turno, (valor[0], valor[1], valor[2], day, position, c), positions_for_horaries):
                    add.append((valor[0], valor[1], valor[2], day, position, c))
                else:
                    remove.append((valor[0], valor[1], valor[2], day, position, c))
        else:
            if valid_positions(quadro, turma, turno, (valor[0], valor[1], day, position), positions_for_horaries):
                add.append((valor[0], valor[1], day, position))
            else:
                remove.append((valor[0], valor[1], day, position))
    return add, remove



def save_board(quadro):
    copy = {}
    for turma in quadro.keys():
        copy[turma] = {
                '2': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],  # manhã e tarde
                '3': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
                '4': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
                '5': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
                '6': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]]
            }
        for dia in quadro[turma].keys():
            for turno in range(0, 3):
                for p in range(0, len(quadro[turma][dia][turno])):
                    if type(quadro[turma][dia][turno][p]) is list:
                        for pb in range(0, len(quadro[turma][dia][turno][p])):
                            if not(type(copy[turma][dia][turno][p]) is list):
                                copy[turma][dia][turno][p] = [0 for c in range(0, len(quadro[turma][dia][turno][p]))]
                            copy[turma][dia][turno][p][pb] = quadro[turma][dia][turno][p][pb]
                    else:
                        copy[turma][dia][turno][p] = quadro[turma][dia][turno][p]
    return copy


def select_turm_and_positions_list(finishing, novo_horario, quadro, typeNum, just_zeros=True):
    if finishing:
            turma = random.choice(list(quadro.keys()))
            positions_for_horaries = generate_list_position(quadro, typeNum, turma=turma, just_zeros=False)
    else:
        # Se estivermos apenas organizando os horários, vamos escolher entre as turmas do professor e do horário em si.
        # Mas vamos dar um maior peso para a turma do professor
        possible_turms = [novo_horario.turm[0] for c in range(0, 8)]
        for teacher_subj in novo_horario.teacher.horaries.values():
            for item in teacher_subj.keys():
                if not (item.split('|')[0] in possible_turms):
                    possible_turms.append(item.split('|')[0])
        
        turma = random.choice(possible_turms)
        positions_for_horaries = generate_list_position(quadro, typeNum, turma=turma, just_zeros=just_zeros)
    
    while len(positions_for_horaries) == 0:
        if not(finishing):
            turma = random.choice(possible_turms)
            positions_for_horaries = generate_list_position(quadro, typeNum, turma=turma, just_zeros=just_zeros)
        else:
            turma = random.choice(list(quadro.keys()))
            positions_for_horaries = generate_list_position(quadro, typeNum, turma=turma, just_zeros=False)
    
    return turma, positions_for_horaries

        
def remove_already_check_positions(positions_for_horaries, already_check, quantiti):
    for c in range(0, len(already_check)//quantiti):
        if already_check[c] in positions_for_horaries:
            positions_for_horaries.remove(already_check[c])
    already_check = []


def TESTANDO_erros(quadro, turma, turno, positions_for_horaries):
    problem = False
    for p in positions_for_horaries:
        if not(valid_positions(quadro, turma, turno, p, positions_for_horaries)):
            problem = True
            #raise Exception('Apareceu um inválido')
    if problem:
        raise Exception('Está dando errado')


def get_weights(lista, quadro, turma, turno, novo_horario, finishing=False):
    pesos = []
    dias_no_mesmo_campus = []
    if finishing:
        pesos = [1 for c in range(0, len(lista))]
        return pesos

    bigger = [0, 0] # [Dia, número de zeros no dia]
    for dia in quadro[turma].keys():
        if bigger[1] < quadro[turma][dia][turno].count(0):
            bigger = [dia, quadro[turma][dia][turno].count(0)]
        elif bigger[1] == quadro[turma][dia][turno].count(0) and bigger[0]:
            n_listas = 0
            for p in range(0, len(quadro[turma][bigger[0]][turno])):
                if type(quadro[turma][bigger[0]][turno][p]) is list:
                    n_listas += 1
                if type(quadro[turma][dia][turno]) is list:
                    n_listas -= 1
            if n_listas < 0:
                bigger = [dia, quadro[turma][dia][turno].count(0)]

        achou = False
        for position in range(0, len(quadro[turma][dia][turno])):
            if quadro[turma][dia][turno][position]:
                if type(quadro[turma][dia][turno][position]) is list:
                    for pb in range(0, len(quadro[turma][dia][turno][position])):
                        if quadro[turma][dia][turno][position][pb]:
                            if quadro[turma][dia][turno][position][pb].local == novo_horario.local:
                                dias_no_mesmo_campus.append(dia)
                                achou = True
                                break

                else:
                    if quadro[turma][dia][turno][position].local == novo_horario.local:
                        dias_no_mesmo_campus.append(dia)
                        achou = True
                        break
            if achou: break

    
    #dias_no_mesmo_campus = []
    if bigger[1]:
        if turma == novo_horario.turm[0]:
            for p in lista:
                if p[0] == bigger[0] and not(bigger[0] in dias_no_mesmo_campus):
                    pesos.append(20)
                elif len(p) == 6 and p[3] == bigger[0]:
                    pesos.append(0.5)
                else:
                    pesos.append(1)
        else:
            for p in lista:
                if len(p) == 4:
                    if quadro[turma][p[0]][turno][p[1]].teacher == novo_horario.teacher:
                        pesos.append(60)
                    else: pesos.append(1)
                else:
                    if quadro[turma][p[0]][turno][p[1]][p[2]].teacher == novo_horario.teacher:
                        pesos.append(60)
                    else: pesos.append(1)

    if len(pesos) == 0:
        pesos = [1 for c in range(0, len(lista))]
    for c in range(0, len(lista)):
            p = lista[c]
            if len(p) == 4:
                pesos[c] += 1
            else:
                if quadro[turma][p[0]][turno][p[1]].count(0):
                    if type(quadro[turma][p[3]][turno][p[4]]) is list:
                        pesos[c] += (quadro[turma][p[0]][turno][p[1]].count(0)**2) / quadro[turma][p[3]][turno][p[4]].count(0) / 2
                    else:
                        pesos[c] /= 1.5
                    try:
                        if type(quadro[turma][p[3] - 1][turno][p[4]]) is list:
                            if quadro[turma][p[3] - 1][turno][p[4]][p[5]].teacher == quadro[turma][p[0]][turno][p[1]][p[2]].teacher:
                                pesos[c] += 8
                    except: pass
                    try:
                        if type(quadro[turma][p[3] + 1][turno][p[4]]) is list:
                            if quadro[turma][p[3] + 1][turno][p[4]][p[5]].teacher == quadro[turma][p[0]][turno][p[1]][p[2]].teacher:
                                pesos[c] += 8
                    except: pass
                else:
                    pesos[c] += 1
                #if len(quadro[turma][p[3]][turno][p[4]]) == 4 and 
            
    # Se o quadro já estiver praticamente todo preenchido, vamos precisar de outra estratégia para criar os pesos
    # Vamos colocar como mais prováveis de serem selecionadas, os bimestrais que possuem mais zeros na lista.
    
    return pesos


def TESTANDO_POSITIONS(quadro, turma, turno, subjectPos, horario):
    print('Testando...')
    print(horario.local, horario.type, horario.teacher)
    continuar = int(input('Editar? '))
    if continuar != 0:
        dia = str(input('Digite o dia: '))
        position = int(input('Digite a posição: '))
        if not('0' in horario.type):
            bimestral = int(input('Digite a posição bimestral: '))
            valid = validation(horario, (dia, position, bimestral), quadro[turma], subjectPos, turno, turma, 1)
            print(valid[1])
        validation(horario, (dia, position), quadro[turma], subjectPos, turno, turma, 0)
        print(valid[1])


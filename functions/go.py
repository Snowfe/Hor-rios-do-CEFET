from functions import loadData
from functions import classes as c
from functions import result
from functions import logic
import random
import copy

NUMERO_DE_REPETIÇÕES = 1
NUMERO_DE_REPETIÇÕES_OP = 100
LIMITE = 20

def organizando_dados_da_planilha():
    # =================== Pegando os dados que nós fornecemos
    try:
        teachersData = loadData.getDatabase('Planilha dos horários.xlsx') ##  # Leitura inicial da planilha
        # A biblioteca substitui o NA por 0, assim, o seguinte código coloca de volta os nomes dos subgrupos que foram substituidos
        for i in range(0, len(teachersData['Sub-Grupo'])):
            if str(teachersData['Sub-Grupo'][i]) == '0':
                teachersData['Sub-Grupo'][i] = 'NA'
        teachersColumns = loadData.getDatabase('Planilha dos horários.xlsx', get="columns") ##
        roomsData = loadData.getDatabase('Planilha sala.xlsx') # Leitura inicial da planilha de salas
        pointsData = loadData.getPoints('./data/preferencias.txt')  # Leitura das pontuações para o cost
    except Exception as e:
        print(f"Houve um erro ao tentar pegar os dados das planilhas.\n{e}")

    # ==================== Processando os dados para deixa-los melhor de mexer

    classesNames = []  # -- Turmas
    classes = []  # Lista de objetos de cada turma

    for i in range(8, len(teachersColumns)):  # Pega apenas as matérias
        classesNames.append(teachersColumns[i])

    for index, turm in enumerate(classesNames):  # Transforma cada turma em um objeto de uma classe
        for i in range(1, 4):  # Turma para cada ano
            for group in ['A', 'B', 'NA', 'NB']:  # Adiciona os subgrupos A e B para todas as turmas
                classes.append(c.Turm(turm, str(i), group))

    teachersNames = []  # -- Professores
    teachers = []  # Lista de objetos de cada professor

    for index, teacher in enumerate(teachersData["Professor"]):  # Transforma cada professor em um objeto de uma classe
        horaries = {}  # Horários para cada turma e matéria
        for i in range(12, len(teachersColumns)):   # SE ACRESCENTAR OU TIRAR COLUNA NA TABELA, TEM QUE MUDAR O VALOR AQUI
            horaries[
                    f"{teachersColumns[i]}-" + 
                    f'{teachersData["Ano"][index]}' + 
                    f'{teachersData["Sub-Grupo"][index]}' + 
                    f'|{int(teachersData["Numero de grupos"][index])},{int(teachersData["Numero de bimestres"][index])},{teachersData["Grupo"][index]}'] = int(
                teachersData[f"{teachersColumns[i]}"][index])


        if not (teacher in teachersNames):
            teachers.append(c.Teacher(teacher,
                                      f'{teachersData["Materia"][index]}-{teachersData["Ano"][index]}{teachersData["Sub-Grupo"][index]}',
                                      f'{teachersData["Tipo"][index]}', 
                                      str(teachersData["Preferencias"][index]).split('-'),
                                      str(teachersData["Limitacoes"][index]).split('-'),
                                      str(teachersData["Bimestral"][index]),
                                      str(teachersData["Local"][index]), 
                                      horaries))
            teachersNames.append(teacher)
        else:
            teachers[teachersNames.index(teacher)].subjects.append(
                f'{teachersData["Materia"][index]}-{teachersData["Ano"][index]}{teachersData["Sub-Grupo"][index]}')
            teachers[teachersNames.index(teacher)].types.append(f'{teachersData["Tipo"][index]}')
            teachers[teachersNames.index(teacher)].prefers.append(str(teachersData["Preferencias"][index]).split('-'))
            teachers[teachersNames.index(teacher)].limits.append(str(teachersData["Limitacoes"][index]).split('-'))
            teachers[teachersNames.index(teacher)].bimestral.append(int(str(teachersData["Bimestral"][index])[0]))
            teachers[teachersNames.index(teacher)].locais.append(str(teachersData["Local"][index]))
            teachers[teachersNames.index(teacher)].horaries[
                f'{teachersData["Materia"][index]}-{teachersData["Ano"][index]}{teachersData["Sub-Grupo"][index]}'] = horaries

        # print(f'{teachers[teachersNames.index(teacher)].name}, {teachers[teachersNames.index(teacher)].horaries}')
    tipos_normais = ['1,4,T', '3,1,G', '2,1,T', '2,2,T', '2,4,T', '0,0,0', '3,4,G']
    for professor in teachers:
        horarios = professor.horaries
        for i, h in enumerate(horarios.items()):
            materia = h[0]
            for turma in h[1].items():
                turma_do_horario = turma[0]
                for time in range(0, turma[1]):
                    sala, tipo = turma[0].split('|')
                    # Esse if só está aqui porque não se sabe ainda como interpretar na tabela final como ficariam os horários de tipos diferentes.
                    # Mas mesmo sem esse horários continua dando o mesmo erro
                    if not(tipo in tipos_normais):
                        #print('tipo', tipo, professor, materia, sala, turma[1])
                        pass
                    else:
                        ho = c.Horario(teacher=professor, subject=materia, turm=(sala, turma[1]), local=professor.locais[i], tipo=tipo)  # Objeto do horário
                        professor.h_individuais.append(ho)  # Uma lista com todos os objetos Horario do professor []
            #professor.h_individuais = loadData.organize_table(professor.h_individuais)

    return teachers, teachersNames


def restartObjects(listO):
    for t in listO:
        t.schedule = {
            '2': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],  # manhã, tarde e noite
            '3': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
            '4': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
            '5': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
            '6': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]]
        }

    return listO


def mainFunction():  # A função principal do código, que retornará o resultado que nós esperamos
    # =================== Pegando os dados que nós fornecemos
    try:
        teachersData = loadData.getDatabase('Planilha dos horários.xlsx') ##  # Leitura inicial da planilha
        # A biblioteca substitui o NA por 0, assim, o seguinte código coloca de volta os nomes dos subgrupos que foram substituidos
        for i in range(0, len(teachersData['Sub-Grupo'])):
            if str(teachersData['Sub-Grupo'][i]) == '0':
                teachersData['Sub-Grupo'][i] = 'NA'
        teachersColumns = loadData.getDatabase('Planilha dos horários.xlsx', get="columns") ##
        roomsData = loadData.getDatabase('Planilha sala.xlsx') # Leitura inicial da planilha de salas
        pointsData = loadData.getPoints('./data/preferencias.txt')  # Leitura das pontuações para o cost
    except Exception as e:
        print(f"Houve um erro ao tentar pegar os dados das planilhas.\n{e}")

    # ==================== Processando os dados para deixa-los melhor de mexer

    classesNames = []  # -- Turmas
    classes = []  # Lista de objetos de cada turma

    for i in range(8, len(teachersColumns)):  # Pega apenas as matérias
        classesNames.append(teachersColumns[i])

    for index, turm in enumerate(classesNames):  # Transforma cada turma em um objeto de uma classe
        for i in range(1, 4):  # Turma para cada ano
            for group in ['A', 'B', 'NA', 'NB']:  # Adiciona os subgrupos A e B para todas as turmas
                classes.append(c.Turm(turm, str(i), group))

    teachersNames = []  # -- Professores
    teachers = []  # Lista de objetos de cada professor

    for index, teacher in enumerate(teachersData["Professor"]):  # Transforma cada professor em um objeto de uma classe
        horaries = {}  # Horários para cada turma e matéria
        for i in range(12, len(teachersColumns)):   # SE ACRESCENTAR OU TIRAR COLUNA NA TABELA, TEM QUE MUDAR O VALOR AQUI
            horaries[
                    f"{teachersColumns[i]}-" + 
                    f'{teachersData["Ano"][index]}' + 
                    f'{teachersData["Sub-Grupo"][index]}' + 
                    f'|{int(teachersData["Numero de grupos"][index])},{int(teachersData["Numero de bimestres"][index])},{teachersData["Grupo"][index]}'] = int(
                teachersData[f"{teachersColumns[i]}"][index])


        if not (teacher in teachersNames):
            teachers.append(c.Teacher(teacher,
                                      f'{teachersData["Materia"][index]}-{teachersData["Ano"][index]}{teachersData["Sub-Grupo"][index]}',
                                      f'{teachersData["Tipo"][index]}', 
                                      str(teachersData["Preferencias"][index]).split('-'),
                                      str(teachersData["Limitacoes"][index]).split('-'),
                                      str(teachersData["Bimestral"][index]),
                                      str(teachersData["Local"][index]), 
                                      horaries))
            teachersNames.append(teacher)
        else:
            teachers[teachersNames.index(teacher)].subjects.append(
                f'{teachersData["Materia"][index]}-{teachersData["Ano"][index]}{teachersData["Sub-Grupo"][index]}')
            teachers[teachersNames.index(teacher)].types.append(f'{teachersData["Tipo"][index]}')
            teachers[teachersNames.index(teacher)].prefers.append(str(teachersData["Preferencias"][index]).split('-'))
            teachers[teachersNames.index(teacher)].limits.append(str(teachersData["Limitacoes"][index]).split('-'))
            teachers[teachersNames.index(teacher)].bimestral.append(int(str(teachersData["Bimestral"][index])[0]))
            teachers[teachersNames.index(teacher)].locais.append(str(teachersData["Local"][index]))
            teachers[teachersNames.index(teacher)].horaries[
                f'{teachersData["Materia"][index]}-{teachersData["Ano"][index]}{teachersData["Sub-Grupo"][index]}'] = horaries

        # print(f'{teachers[teachersNames.index(teacher)].name}, {teachers[teachersNames.index(teacher)].horaries}')
    tipos_normais = ['1,4,T', '3,1,G', '2,1,T', '2,2,T', '2,4,T', '0,0,0', '3,4,G']
    for professor in teachers:
        horarios = professor.horaries
        for i, h in enumerate(horarios.items()):
            materia = h[0]
            for turma in h[1].items():
                turma_do_horario = turma[0]
                for time in range(0, turma[1]):
                    sala, tipo = turma[0].split('|')
                    # Esse if só está aqui porque não se sabe ainda como interpretar na tabela final como ficariam os horários de tipos diferentes.
                    # Mas mesmo sem esse horários continua dando o mesmo erro
                    if not(tipo in tipos_normais):
                        #print('tipo', tipo, professor, materia, sala, turma[1])
                        pass
                    else:
                        ho = c.Horario(teacher=professor, subject=materia, turm=(sala, turma[1]), local=professor.locais[i], tipo=tipo)  # Objeto do horário
                        professor.h_individuais.append(ho)  # Uma lista com todos os objetos Horario do professor []
            professor.h_individuais = loadData.organize_table(professor.h_individuais)

    roomsNames = roomsData['Sala'] # -- Salas
    rooms = []

    for index, room in enumerate(roomsNames):  # Transforma cada turma em um objeto de uma classe
        rooms.append(c.Room(room, roomsData['Local'][index], roomsData['Limitacoes'][index]))

    # ==================== Processando os dados: Gerando a planilha final com base nos dados

    bestSchedule = []
    # Duplicar os objetos professores e manipular apenas umgrupo nessa parte a baixo
    for time in range(0, NUMERO_DE_REPETIÇÕES):
        print('.', end=' ')
        ERRO_NOS_HORARIOS = False
        teachers_copy = restartObjects(teachers)

        # Embaralha a lista de professores
        lista_embaralhada = teachers.copy()
        random.shuffle(lista_embaralhada)

        # Quadro de horários em branco
        quadro = {}
        for turm in classes:
            quadro[turm.name] = {
                '2': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],  # manhã e tarde
                '3': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
                '4': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
                '5': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
                '6': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]]
            }

            # Preencher horários já preenchidos com algo diferente de 0

        while len(lista_embaralhada) != 0:
            print('-')
            # Retiro o primeiro item da lista e o coloco na variável teacher
            teacher = lista_embaralhada[0]
            lista_embaralhada = lista_embaralhada[1:]
            # lista com os objetos horários do professores
            h_professor = teacher.h_individuais

            for horario in h_professor:
                subjectPos = horario.teacher.subjects.index(f"{horario.subject}")  # -{horario.turm[0].split('-')[1]}")
               
                typeV = horario.teacher.types[subjectPos]
                typeNum = 0
                if typeV == 'Tarde': typeNum = 1
                elif typeV == 'Noite': typeNum = 2
                # Seleciono qual o melhor estado para aquele horário

                position, motivo = logic.getBetterHour(horario, quadro.copy()[horario.turm[0]], subjectPos,
                                                typeNum)  # type é 0 - manha ou 1 - tarde. retorna 'day;hour;turm;room' 
                if position == 'ERROR':
                    print('Optimizando...', end='')
                    new_board, position_optmizer = Optmizer(quadro,teachers, horario, subjectPos, typeNum)
                    position = position_optmizer

                    #print(position, '<->', horario.turm)

                    teste = position.split(';')
                    """
                    if len(teste) == 4:
                        #print(new_board[teste[3]])
                        #print(new_board[teste[3]][teste[0]])
                        #print(new_board[teste[3]][teste[0]][typeNum])
                        print(new_board[teste[3]][teste[0]][typeNum][int(teste[1])])
                        if new_board[teste[3]][teste[0]][typeNum][int(teste[1])]:
                            print(new_board[teste[3]][teste[0]][typeNum][int(teste[1])][int(teste[2])])

                    else:
                        #print(new_board[teste[2]])
                        #print(new_board[teste[2]][teste[0]])
                        #print(new_board[teste[2]][teste[0]][typeNum])
                        print(new_board[teste[2]][teste[0]][typeNum][int(teste[1])])
                    """

                    print('achou!')
                    if new_board == 'Não conseguiu achar um melhor':
                        print(typeNum, f'| ### {motivo} ###')
                        # Vamos printar os valores dos professores também
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
                        ERRO_NOS_HORARIOS = True
                        break 
                    else:
                        quadro = new_board
                        if quadro != new_board:
                            print('Não são iguais')

                position_info = position.split(';')

                # Coloco o horário naquela posição
                if teacher.bimestral[subjectPos] == 1: # Se horário for bimestral
                    if not(type(quadro[position_info[3]][position_info[0]][typeNum][int(position_info[1])]) is list): # Se no horário não for lista, criamos a lista
                        if '1' == horario.type[2]:
                            quadro[position_info[3]][position_info[0]][typeNum][int(position_info[1])] = [0, 0, 0, 0]
                        elif '4,G' in horario.type:
                            quadro[position_info[3]][position_info[0]][typeNum][int(position_info[1])] = [0, 0, 0]
                        elif '2,T' in horario.type or '4,T' in horario.type:
                            quadro[position_info[3]][position_info[0]][typeNum][int(position_info[1])] = [0, 0]
                        
                    # E em seguida colocamos o horário bimestral nessa posição
                    if quadro[position_info[3]][position_info[0]][typeNum][int(position_info[1])][int(position_info[2])] != 0:
                        print(f'HORARIO JÁ OCPUADO:::::::  {quadro[position_info[3]][position_info[0]][typeNum][int(position_info[1])][int(position_info[2])]}, {horario}')
                    try: quadro[position_info[3]][position_info[0]][typeNum][int(position_info[1])][int(position_info[2])] = horario
                    except:
                        print('Posição inválida', position_info, typeNum)
                        print(len(quadro[position_info[3]][position_info[0]][typeNum][int(position_info[1])]), horario, horario.type)
                        print(quadro[position_info[3]][position_info[0]][typeNum])

                        return KeyError
                    
                else:  # Se já for uma lista apenas colocamos o horário na posição mesmo
                    quadro[position_info[2]][position_info[0]][typeNum][int(position_info[1])] = horario

                # Professores
                if teacher.bimestral[subjectPos] == 1: # Se horário for bimestral
                    if not(type(horario.teacher.schedule[position_info[0]][typeNum][int(position_info[1])]) is list): # Se no horário não for lista
                        
                        if '1' == horario.type[2]:
                            horario.teacher.schedule[position_info[0]][typeNum][int(position_info[1])] = [0, 0, 0, 0]
                        elif '4,G' in horario.type:
                            horario.teacher.schedule[position_info[0]][typeNum][int(position_info[1])] = [0, 0, 0]
                        elif '2,T' in horario.type or '4,T' in horario.type:
                            horario.teacher.schedule[position_info[0]][typeNum][int(position_info[1])] = [0, 0]
                    try:

                        horario.teacher.schedule[position_info[0]][typeNum][int(position_info[1])][int(position_info[2])] = f"{horario.turm[0]}-{str(horario).split('-')[1]}"
                    except:
                        print(horario.type, position[2], horario.teacher.schedule[position_info[0]][typeNum][int(position_info[1])], motivo)
                    teachers_copy[teachersNames.index(horario.teacher.name)].schedule[position_info[0]][typeNum][
                        int(position_info[1])] = list(horario.teacher.schedule[position_info[0]][typeNum][int(position_info[1])])
                else:
                    horario.teacher.schedule[position_info[0]][typeNum][int(position_info[1])] = f"{horario.turm[0]}-{str(horario).split('-')[1]}"

                    teachers_copy[teachersNames.index(horario.teacher.name)].schedule[position_info[0]][typeNum][
                        int(position_info[1])] = f"{horario.turm[0]}-{str(horario).split('-')[1]}"

                # Alterando objeto do professor
            if ERRO_NOS_HORARIOS:
                break
        if ERRO_NOS_HORARIOS:
            print(time, 'Inválido')
            continue

        pontuacao = logic.cost_board(quadro)

        
        try:
            if bestSchedule[0][1] == pontuacao:
                bestSchedule.append([quadro.copy(), pontuacao, copy.deepcopy(teachers_copy)])
            elif pontuacao > bestSchedule[0][1]:
                bestSchedule = [[quadro.copy(), pontuacao, copy.deepcopy(teachers_copy)]]
        except:
            bestSchedule.append([quadro.copy(), pontuacao, copy.deepcopy(teachers_copy)])

        print(time, pontuacao)
        break

    horarios = random.choice(bestSchedule)

    for turm in classes:
        result.saveSheet(turm.name, horarios[0][turm.name], type='turm')
    for teacher in teachers:
        result.saveSheet(teacher.name, horarios[2][teachersNames.index(teacher.name)].schedule, type='teacher')


def Optmizer(quadro_base, teachers, novo_horario=None, subjectPos=0, typeNum=0, finishing=False):
    """
    finishing => Essa função poder ser usada para organizar os horários durante a criação,
                 de modo que quando o horário que não possuia lugar já possuir um lugar para ser colocado, nós retornamos e paramos o código
                 Seu segundo uso é para quando já terminamos de organizar o quadro, e portanto podemos apenas usar a função para melhorar o resultado final.
    """
    keep_going = True
    times = 0
    # Inicialmos com uma grade horária funcional
    #lista_com_objt_professores, lista_com_nomes_professores = organizando_dados_da_planilha()
    #quadro = loadData.get_functional_grade('Planilha funcional', teachers=lista_com_objt_professores, teachersNames=lista_com_nomes_professores)

    # Embaralhamos ela mantendo a sua funcionalidade
    #quadro_base = logic.messi_data(quadro)
    
    quadro = quadro_base.copy()

    teachers_copy = copy.deepcopy(teachers)
    better_board = (quadro_base, logic.cost_board(quadro_base), teachers_copy)

    # Começamos a organizá-la
    while keep_going:
        print('.', end='')
        times += 1
        find_one_better = False
        # Criamos a cópia do quadro
        quadro = better_board[0]
        #better_board = (quadro_base, logic.cost_board(quadro_base), teachers) # ???
        logic.actualize(teachers, better_board[2])
        
        # Vamos selecionar aletóriamente 10 horários de uma turma e misturar a posição deles
        for time in range(0, int(20 + better_board[1] // 500)): # vezes que vamos realizar a mudança em um horário
            de_acordo = False
            bimestral_2_is_zero = False
            # Escolhemos uma turma aleatória onde faremos as mudanças
            if finishing:
                turma = random.choice(list(quadro_base.keys()))
            else:
                possible_classes = [novo_horario.turm[0]]
                for teacher_subj in novo_horario.teacher.horaries.values():
                    for item in teacher_subj.keys():
                        if not (item in possible_classes):
                            possible_classes.append(item.split('|')[0])
                #print(possible_classes)
                turma = random.choice(possible_classes)

            # Escolhemos um horário específico dessa turma
            dia_1 = random.choice(list(quadro[turma].keys()))
            turno = random.randint(0, 2)
            p_1 = random.randint(0, len(quadro[turma][dia_1][turno])-1)
            horario_1 = quadro[turma][dia_1][turno][p_1]
            if not(horario_1): # Esse horário não pode estar vazio
                time -= 1
                #print('voltou (1)', end='')
                continue

            # Se for uma lista, selecionamos um horário específico dentre os bimestrais
            if type(horario_1) is list:
                for c_bimestral in range(0, 4):
                    pb_1 =  random.randint(0, len(horario_1)-1)
                    h_bimestral_1 = horario_1[pb_1]
                    if h_bimestral_1: # Ele também não pode ser 0
                        break
                if c_bimestral == 3:
                    continue
                for c in range(0, 24):  # Número arbitrário de repetições para achar um horário válido
                    # Selecionamos o segundo horário

                    dia_2 = random.choice(list(quadro[turma].keys()))
                    p_2 = random.randint(0, len(quadro[turma][dia_2][turno])-1)
                    horario_2 = quadro[turma][dia_2][turno][p_2]

                    # Se os horários forem de mesmo tipo poderemos trocar os dois de lugar
                    if type(horario_2) is list:
                        pb_2 = random.randint(0, len(horario_2)-1)
                        h_bimestral_2 = horario_2[pb_2]
                        if h_bimestral_2 == 0:
                            de_acordo = True
                            bimestral_2_is_zero = True
                        elif h_bimestral_1.type == h_bimestral_2.type:
                            de_acordo = True
                        if de_acordo: # se o outro for 0 ou se for do mesmo tipo podemos trocar
                            # Vemos se é válido trocar os dois horários de posição
                            subjectPos_1 = h_bimestral_1.teacher.subjects.index(f"{h_bimestral_1.subject}")
                            if not(bimestral_2_is_zero):
                                subjectPos_2 = h_bimestral_2.teacher.subjects.index(f"{h_bimestral_2.subject}")
                            
                            quadro[turma][dia_1][turno][p_1][pb_1] = 0
                            quadro[turma][dia_2][turno][p_2][pb_2] = 0

                            h_bimestral_1.teacher.schedule[dia_1][turno][p_1][pb_1] = 0

                            try: h_bimestral_2.teacher.schedule[dia_2][turno][p_2][pb_2] = 0
                            except: pass # Se o horário for 0 iria dar erro

                            if turno == 2 and p_2 >= 4: print('Horario errado -> ', p_2,' -- ', horario_2)
                            valid_1 = logic.validation(h_bimestral_1, (dia_2, p_2, pb_2), quadro[turma], subjectPos_1,turno, 1)
                            # Se for, mudamos no quadro e na tabela e no dos professores
                            if valid_1[0] == 0:
                                try:
                                    if turno == 2 and p_2 >= 4: print('Horario errado -> ', p_1,' -- ', horario_1)
                                    valid_2 = logic.validation(h_bimestral_2, (dia_1, p_1, pb_1), quadro[turma], subjectPos_2,turno, 1)
                                except: valid_2 = 0, 0
                                if valid_2[0] == 0:
                                    # Colocamos os horários nas respectivas posições
                                    quadro[turma][dia_1][turno][p_1][pb_1] = h_bimestral_2
                                    quadro[turma][dia_2][turno][p_2][pb_2] = h_bimestral_1
                                    h_bimestral_1.teacher.schedule[dia_1][turno][p_1][pb_1] = h_bimestral_2
                                    try: h_bimestral_2.teacher.schedule[dia_2][turno][p_2][pb_2] = h_bimestral_1
                                    except: pass
                                else: # Se não for valido, recolocamos na posição horiginal
                                    quadro[turma][dia_1][turno][p_1][pb_1] = h_bimestral_1
                                    quadro[turma][dia_2][turno][p_2][pb_2] = h_bimestral_2
                                    h_bimestral_1.teacher.schedule[dia_1][turno][p_1][pb_1] = h_bimestral_1
                                    try: h_bimestral_2.teacher.schedule[dia_2][turno][p_2][pb_2] = h_bimestral_2
                                    except: pass
                            else: # Se não for valido, recolocamos na posição horiginal
                                quadro[turma][dia_1][turno][p_1][pb_1] = h_bimestral_1
                                quadro[turma][dia_2][turno][p_2][pb_2] = h_bimestral_2
                                h_bimestral_1.teacher.schedule[dia_1][turno][p_1][pb_1] = h_bimestral_1
                                try: h_bimestral_2.teacher.schedule[dia_2][turno][p_2][pb_2] = h_bimestral_2
                                except: pass
                        
                            # Vemos se essa mudança é o bastante para que o outro horário já possa ser colocado
                            if not(finishing):
                                position, motivo = logic.getBetterHour(novo_horario, quadro[novo_horario.turm[0]], subjectPos, typeNum)
                                if position != 'ERROR':
                                    #print('passando por aqui 4')
                                    print(turma, position)
                                    return quadro, position

                            # Se a nova configuração for melhor, usamos ela como padrão
                            value = logic.cost_board(quadro)
                            if value >= better_board[1]:
                                teachers_version = copy.deepcopy(teachers)
                                better_board = (quadro, value, teachers_version)
                                find_one_better = True
                            
                            break
                        else:
                            time -= 1
                            #print('voltou (2)', end='')
                            continue
                    elif not(horario_2) and type(horario_1) is list:
                        # Se o segundo horário for 0, não precisamos fazer algumas coisas nele
                        subjectPos_1 = h_bimestral_1.teacher.subjects.index(f"{h_bimestral_1.subject}") 

                        quadro[turma][dia_1][turno][p_1][pb_1] = 0
                        h_bimestral_1.teacher.schedule[dia_1][turno][p_1][pb_1] = 0

                        pb_2 = random.randint(0, 3)
                        
                        if turno == 2 and p_2 >= 4: print('Horario errado -> ', p_2,' -- ', horario_2)
                        valid_1 = logic.validation(h_bimestral_1, (dia_2, p_2, pb_2), quadro[turma], subjectPos_1,turno, 1)
                        if valid_1[0] == 0:
                            # Criamos a lista nessa posição
                            if '1' == h_bimestral_1.type[2]:
                                quadro[turma][dia_2][turno][p_2] = [0, 0, 0, 0]
                                if not(h_bimestral_1.teacher.schedule[dia_2][turno][p_2]): h_bimestral_1.teacher.schedule[dia_2][turno][p_2] = [0, 0, 0, 0]
                            elif '4,G' in h_bimestral_1.type:
                                quadro[turma][dia_2][turno][p_2] = [0, 0, 0]
                                if not(h_bimestral_1.teacher.schedule[dia_2][turno][p_2]): h_bimestral_1.teacher.schedule[dia_2][turno][p_2] = [0, 0, 0]
                            else:
                                quadro[turma][dia_2][turno][p_2] = [0, 0]
                                if not(h_bimestral_1.teacher.schedule[dia_2][turno][p_2]): h_bimestral_1.teacher.schedule[dia_2][turno][p_2] = [0, 0]
                            # Colocamos o horário na posição
                            quadro[turma][dia_2][turno][p_2][0] = h_bimestral_1
                        else:
                            quadro[turma][dia_1][turno][p_1][pb_1] = h_bimestral_1
                            if quadro[turma][dia_1][turno][p_1].count(0) == len(quadro[turma][dia_1][turno][p_1]):
                                quadro[turma][dia_1][turno][p_1] = 0

            else: # Horários normais
                for c in range(0, 24):  # Número arbitrário de repetições para achar um horário válido

                    # Selecionamos o segundo horário
                    dia_2 = random.choice(list(quadro[turma].keys()))
                    turno = random.randint(0, 2)
                    p_2 = random.randint(0, len(quadro[turma][dia_2][turno])-1)
                    horario_2 = quadro[turma][dia_2][turno][p_2]
                    if type(horario_2) is list:
                        continue
                    

                    # Se os horários forem de mesmo tipo poderemos trocar os dois de lugar
                    if not(horario_2) or (type(horario_1) == type(horario_2)):
                        # Vemos se é válido trocar os dois horários de posição
                        if horario_1: 
                            subjectPos_1 = horario_1.teacher.subjects.index(f"{horario_1.subject}")
                            #print(quadro[turma][dia_1][turno])
                            quadro[turma][dia_1][turno][p_1] = 0
                            horario_1.teacher.schedule[dia_1][turno][p_1] = 0

                        if horario_2: 
                            subjectPos_2 = horario_2.teacher.subjects.index(f"{horario_2.subject}") 
                            quadro[turma][dia_2][turno][p_2] = 0
                            horario_2.teacher.schedule[dia_2][turno][p_2] = 0
                        if turno == 2 and p_2 >= 4: print('Horario errado -> ', p_2,' -- ', horario_2)
                        valid_1 = logic.validation(horario_1, (dia_2, p_2), quadro[turma], subjectPos_1,turno, 1)
                        # Se for, mudamos no quadro e na tabela e no dos professores
                        if valid_1[0] == 0:
                            try: valid_2 = logic.validation(horario_2, (dia_1, p_1), quadro[turma], subjectPos_2,turno, 1)
                            except: valid_2 = (0, 0)
                            if valid_2[0] == 0:
                                # Colocamos os horários nas respectivas posições
                                quadro[turma][dia_1][turno][p_1] = horario_2
                                quadro[turma][dia_2][turno][p_2] = horario_1
                                horario_1.teacher.schedule[dia_2][turno][p_2] = horario_1
                                try: horario_2.teacher.schedule[dia_1][turno][p_1] = horario_1
                                except: pass
                            else: # Se não for valido, recolocamos na posição horiginal
                                quadro[turma][dia_1][turno][p_1] = horario_1
                                quadro[turma][dia_2][turno][p_2] = horario_2
                                horario_1.teacher.schedule[dia_1][turno][p_1] = horario_1
                                try: horario_2.teacher.schedule[dia_2][turno][p_2] = horario_2
                                except: pass
                        else: # Se não for valido, recolocamos na posição horiginal
                            quadro[turma][dia_1][turno][p_1] = horario_1
                            quadro[turma][dia_2][turno][p_2] = horario_2
                            horario_1.teacher.schedule[dia_1][turno][p_1] = horario_1
                            try: horario_2.teacher.schedule[dia_2][turno][p_2] = horario_2
                            except: pass
                    
                        # Vemos se essa mudança é o bastante para que o outro horário já possa ser colocado
                        if not(finishing):
                            position, motivo = logic.getBetterHour(novo_horario, quadro[novo_horario.turm[0]], subjectPos, typeNum)
                            if position != 'ERROR':
                                #print('passando por aqui 3')
                                print(position)
                                return quadro, position

                        # Se a nova configuração for melhor, usamos ela como padrão
                        value = logic.cost_board(quadro)
                        if value >= better_board[1]:
                            teachers_version = copy.deepcopy(teachers)
                            better_board = (quadro, value, teachers_version)
                            find_one_better = True
        if finishing:
            if not(find_one_better):
                logic.actualize(teachers, better_board[2])
                #print('passando por aqui 2')
                return better_board[0], 0
        else:
            if times == LIMITE + int(better_board[1] / 100):
                #print('passando por aqui 1')
                return 'Não conseguiu achar um melhor', 0
            
    #print('passando pelo final')
    logic.actualize(teachers, better_board[2])  
    return better_board[0], 0



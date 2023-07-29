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

    for i in range(12, len(teachersColumns)):  # Pega apenas as matérias
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
            #print('-')
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
                    new_board, position = Optmizer(quadro,teachers, horario, subjectPos, typeNum)
                    if type(position) is int:
                        print('Position:: INT', position)

                    #print(position, '<->', horario.turm)

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
                    print('.')
                    print('achou!')
                    if new_board == 'Não conseguiu achar um melhor':
                        print(typeNum, f'| ### {motivo} ###')
                        # Vamos printar os valores dos professores também
                        logic.print_quadro(quadro, horario, typeNum)
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
    # Primeiramente, vamos ver se não tem nada de errado nas informações que estamos recebendo.
    already_check = []
    times = 0
    # Inicialmos com uma grade horária funcional
    quadro = quadro_base.copy()
    better_board = (logic.save_board(quadro), logic.cost_board(quadro_base), copy.deepcopy(teachers))

    for d in quadro[novo_horario.turm[0]].keys():
        for p in range(0, len(quadro[novo_horario.turm[0]][d][typeNum])):
            if type(quadro[novo_horario.turm[0]][d][typeNum][p]) is list:
                for b in range(0, len(quadro[novo_horario.turm[0]][d][typeNum][p])):
                    try:
                        if quadro[novo_horario.turm[0]][d][typeNum][p][b].teacher.schedule[d][typeNum][p][b] in quadro[novo_horario.turm[0]][d][typeNum][p][b]:
                            print(quadro[novo_horario.turm[0]][d][typeNum][p][b].teacher.schedule[d][typeNum][p], quadro[novo_horario.turm[0]][d][typeNum][p])

                    except: pass
            else:
                try:
                    if quadro[novo_horario.turm[0]][d][typeNum][p][b].teacher.schedule[d][typeNum][p] in quadro[novo_horario.turm[0]][d][typeNum][p]:
                        print('*', end='')
                except: pass


    # Começamos a organizá-la
    while True:
        #logic.print_quadro(quadro, novo_horario, typeNum)
        #print('================================================================')
        print('.', end='')
        if '0' in novo_horario.type:
            print('NORMAL', end='')
        else:
            print('BIMESTRAL', end='')
        times += 1
        find_one_better = False
        # Criamos a cópia do quadro, continuamos atualizando o melhor estado
        quadro = logic.save_board(better_board[0])
        logic.actualize(teachers, better_board[2])
        #logic.print_quadro(quadro, novo_horario, typeNum)

        if finishing:
                turma = random.choice(list(quadro_base.keys()))
                positions_for_horaries = logic.generate_list_position(better_board[0], typeNum, turma=turma)
        else:
            # Se estivermos apenas organizando os horários, vamos escolher entre as turmas do professor e do horário em si.
            # Mas vamos dar um maior peso para a turma do professor
            possible_turms = [novo_horario.turm[0], novo_horario.turm[0], novo_horario.turm[0], novo_horario.turm[0]]
            for teacher_subj in novo_horario.teacher.horaries.values():
                for item in teacher_subj.keys():
                    if not (item.split('|')[0] in possible_turms):
                        possible_turms.append(item.split('|')[0])
            
            turma = random.choice(possible_turms)
            #print(' turma escolhida é -> ', turma, ' ')
            #print(f' Novas possiveis turmas encontradas {len(possible_turms) - 5}')
            positions_for_horaries = logic.generate_list_position(quadro, typeNum, turma=turma)
            while len(positions_for_horaries) == 0:
                turma = random.choice(possible_turms)
                positions_for_horaries = logic.generate_list_position(quadro, typeNum, turma=turma)
        
        #turma = novo_horario.turm[0]
        turno = typeNum

        for c in range(0, len(already_check)//4):
            if already_check[c] in positions_for_horaries:
                positions_for_horaries.remove(already_check[c])
        already_check = []
        # Vamos selecionar aletóriamente 10 horários de uma turma e misturar a posição deles
        for time in range(1, int(50 + len(positions_for_horaries) // 8)): # vezes que vamos realizar a mudança em um horário
            print(f'_', end='')
            if len(positions_for_horaries) == 0:
                break
            # Se tivermos encontrado uma posição melhor, permitimos que o código rode mais vezes, além de atualizarmos as posições
            if find_one_better or time % int(300) == 0:
                print(f'{len(positions_for_horaries)} -> ', end=' ')
                positions_for_horaries = logic.generate_list_position(quadro, typeNum, turma=turma)
                if not(find_one_better):
                    for c in range(0, len(already_check)//2):
                        if already_check[c] in positions_for_horaries:
                            positions_for_horaries.remove(already_check[c])
                already_check = []
                print(len(positions_for_horaries))
                find_one_better = False
            
            zero_days = logic.days_with_zero(quadro, turno, turma)
            to_remove = []

            for p in positions_for_horaries:
                if len(p) == 6:
                    if not(p[0] in zero_days) and not(p[3] in zero_days):
                        to_remove.append(p)
                else:
                    if not(p[0] in zero_days) and not(p[3] in zero_days):
                        to_remove.append(p)
            for p in to_remove:
                positions_for_horaries.remove(p)
            
            for p in positions_for_horaries:
                if not(logic.valid_positions(quadro, turma, turno, p, positions_for_horaries)):
                    raise Exception('Apareceu um inválido')
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
            
            # Ainda podemos criar outro processo para selecionarmos o turno e a turma com base nas turmas que o professor da aula ou até mesmo todas elas
            #turma = novo_horario.turm[0]
            turno = typeNum
            # Escolhemos um horário específico dessa turma
            
            random_one = random.choice(positions_for_horaries)
            positions_for_horaries.remove(random_one)
            already_check.append(random_one)
            for p in positions_for_horaries:
                if not(logic.valid_positions(quadro, turma, turno, p, positions_for_horaries)):
                    raise Exception('Apareceu um inválido')
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
            if random_one in positions_for_horaries:
                print('Ainda está aqui!!!, ', positions_for_horaries.count(random_one))
            
            if len(random_one) == 6:
                dia_1 = random_one[0]
                p_1 = random_one[1]
                pb_1 = random_one[2]
                dia_2 = random_one[3]
                p_2 = random_one[4]
                pb_2 = random_one[5]
                horario_1 = quadro[turma][dia_1][turno][p_1]
                horario_2 = quadro[turma][dia_2][turno][p_2]
                h_bimestral_1 = quadro[turma][dia_1][turno][p_1][pb_1]
                try:                  
                    if quadro[turma][dia_2][turno][p_2] == 0: h_bimestral_2 = 0
                    else:
                        try:
                            h_bimestral_2 = quadro[turma][dia_2][turno][p_2][pb_2]  
                        except:
                            ERRO = quadro[turma][dia_2][turno][p_2]
                            h_bimestral_2 = quadro[turma][dia_2][turno][p_2][pb_2]
                except:
                    print(horario_2, 'TURMA ==>', turma)
                    h_bimestral_2 = quadro[turma][dia_2][turno][p_2][pb_2] 
                
                #try: h_bimestral_2 = quadro[turma][dia_2][turno][p_2][pb_2]
                #except:  h_bimestral_2 = 0
                try:
                    subjectPos_1 = h_bimestral_1.teacher.subjects.index(f"{h_bimestral_1.subject}")
                except:
                    print(f'H1 não foi ({dia_1, p_1})')
                    subjectPos_1 = h_bimestral_1.teacher.subjects.index(f"{h_bimestral_1.subject}")
                try: subjectPos_2 = h_bimestral_2.teacher.subjects.index(f"{h_bimestral_2.subject}")
                except: pass # Vai acontecer quando for 0
                if not(str(h_bimestral_1.teacher.schedule[dia_1][turno][p_1][pb_1]).split('-')[-1] in str(h_bimestral_1)):
                    print(f'Na hora de gerar, o do professor já não é o mesmo que o horario, BIMESTRAL1, professor: {h_bimestral_1.teacher.schedule[dia_1][turno][p_1][pb_1]}, quadro: {h_bimestral_1}')
                try:
                    if not(str(h_bimestral_2.teacher.schedule[dia_2][turno][p_2][pb_2]).split('-')[-1] in str(h_bimestral_2)):
                        print(f'Na hora de gerar, o do professor já não é o mesmo que o horario, BIMESTRAL2, professor{h_bimestral_2.teacher.schedule[dia_2][turno][p_2][pb_2]}, quadro: {h_bimestral_2}')
                except: pass
                
            else:   
                dia_1 = random_one[0]
                p_1 = random_one[1]
                dia_2 = random_one[2]
                p_2 = random_one[3]
                horario_1 = quadro[turma][dia_1][turno][p_1]
                if not horario_1:
                    print('Horario 1 é 0')
                    print(f'TURMA H1 ({dia_1, p_1})==> ', turma)
                horario_2 = quadro[turma][dia_2][turno][p_2]
                try:
                    subjectPos_1 = horario_1.teacher.subjects.index(f"{horario_1.subject}")
                except:
                    print(horario_1)
                try: subjectPos_2 = horario_2.teacher.subjects.index(f"{horario_2.subject}")
                except: pass # Vai acontecer quando for 0
                if not(str(horario_1.teacher.schedule[dia_1][turno][p_1]).split('-')[-1] in str(horario_1)):
                    print(f'Na hora de gerar, o do professor já não é o mesmo que o horario, NORMAL, professor{horario_1.teacher.schedule[dia_1][turno][p_1]}, quadro: {horario_1}')
                try:
                    if not(str(horario_2.teacher.schedule[dia_2][turno][p_2]).split('-')[-1] in str(horario_2)):
                        print(f'Na hora de gerar, o do professor já não é o mesmo que o horario, NORMAL, professor: {horario_2.teacher.schedule[dia_2][turno][p_2]}, quadro: {horario_2}')
                except: pass
            
            if len(random_one) == 6: # Vamos trocar dois bimestrais de posição
                TESTE_passou_pela_troca = False
                TESTE_passou_pela_reposition = False
                """
                for p in positions_for_horaries:
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
                # Fazemos os dois serem 0, necessário para passar pelo validation
                quadro[turma][dia_1][turno][p_1][pb_1] = 0
                h_bimestral_1.teacher.schedule[dia_1][turno][p_1][pb_1] = 0
                if quadro[turma][dia_2][turno][p_2]:
                    if h_bimestral_2 != 0:
                        h_bimestral_2.teacher.schedule[dia_2][turno][p_2][pb_2] = 0
                        quadro[turma][dia_2][turno][p_2][pb_2] = 0
                    
                # Vemos se a mudança de posição é valida
                valid_1 = logic.validation(h_bimestral_1, (dia_2, p_2, pb_2), quadro[turma], subjectPos_1,turno, 1)
                try: valid_2 = logic.validation(h_bimestral_2, (dia_1, p_1, pb_1), quadro[turma], subjectPos_2,turno, 1)
                except: valid_2 = 0, 0 # Vai acontecer no caso em que for 0
                
                # Se for válida trocamos os dois de posição
                if not(valid_1[0]) and not(valid_2[0]): # Caso ambos sejam válidos
                    
                    TESTE_passou_pela_troca = True
                    # Vamos trocar eles de lugar
                    logic.replace_h(quadro, turma, turno, h_bimestral_1, dia_1, p_1, h_bimestral_2, dia_2, p_2,positions_for_horaries, pb_1=pb_1, pb_2=pb_2)

                    positions_for_horaries = logic.actualize_list_posittions(quadro,turma, turno, positions_for_horaries,
                                                                            dia_1, p_1, dia_2, p_2, pb1=pb_1, pb2=pb_2)
                    for p in positions_for_horaries:
                        if not(logic.valid_positions(quadro, turma, turno, p, positions_for_horaries)):
                            raise Exception('Apareceu um inválido')
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
                    for p in positions_for_horaries:
                        try:
                            if quadro[turma][p[0]][turno][p[1]][p[2]]:
                                if not(str(quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]]).split('-')[-1] in str(quadro[turma][p[0]][turno][p[1]][p[2]])):
                                    print('556, depois de colocar o bimestral')
                                    break
                            else:
                                try:
                                    if not(str(quadro[turma][p[3]][turno][p[4]][p[5]].teacher.schedule[p[3]][turno][p[4]][p[5]]).split('-')[-1] in str(quadro[turma][p[3]][turno][p[4]][p[5]])):
                                        print('556, depois de colocar o bimestral')
                                        break
                                except: pass
                        except:
                            if not(str(quadro[turma][p[0]][turno][p[1]].teacher.schedule[p[0]][turno][p[1]]).split('-')[-1] in str(quadro[turma][p[0]][turno][p[1]])):
                                print('556, depois de colocar o bimestral')
                                break
                            else:
                                try:
                                    if not(str(quadro[turma][p[3]][turno][p[4]].teacher.schedule[p[3]][turno][p[4]]).split('-')[-1] in str(quadro[turma][p[3]][turno][p[4]])):
                                        print('556, depois de colocar o bimestral')
                                        break
                                except: pass
                    """
                    # Vemos se é melhor do que o que já temos
                    value = logic.cost_board(quadro)
                    if value > better_board[1]:
                        # Quero manter uma cópia salvae que não varie conforme mudamos as váriáveis tentando achar uma melhor
                        better_board = (logic.save_board(quadro), value, copy.deepcopy(teachers))
                        print('^^^', end='')
                        find_one_better = True
                    
                    # Vemos se já é o bastante para colocar o novo_horario em algum lugar
                    if not(finishing):
                        position, motivo = logic.getBetterHour(novo_horario, quadro[novo_horario.turm[0]], subjectPos, typeNum)
                        if position != 'ERROR':
                            #print('passando por aqui 4')
                            print(turma, position)
                            return quadro, position
                
                else: # Se não for válido deixamos de novo do jeito que era
                    TESTE_passou_pela_reposition = True

                    
                    quadro[turma][dia_1][turno][p_1][pb_1] = h_bimestral_1
                    h_bimestral_1.teacher.schedule[dia_1][turno][p_1][pb_1] = f"{h_bimestral_1.turm[0]}-{str(h_bimestral_1).split('-')[1]}"
                    
                    if quadro[turma][dia_2][turno][p_2]:
                        if h_bimestral_2:
                            quadro[turma][dia_2][turno][p_2][pb_2] = h_bimestral_2
                            h_bimestral_2.teacher.schedule[dia_2][turno][p_2][pb_2] = f"{h_bimestral_2.turm[0]}-{str(h_bimestral_2).split('-')[1]}"
                    """
                    for p in positions_for_horaries:
                        try:
                            if quadro[turma][p[0]][turno][p[1]][p[2]]:
                                if not(str(quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]]).split('-')[-1] in str(quadro[turma][p[0]][turno][p[1]][p[2]])):
                                    print('606, depois de recolocar')
                                    break
                            else:
                                try:
                                    if not(str(quadro[turma][p[3]][turno][p[4]][p[5]].teacher.schedule[p[3]][turno][p[4]][p[5]]).split('-')[-1] in str(quadro[turma][p[3]][turno][p[4]][p[5]])):
                                        print('606, depois de recolocar')
                                        break
                                except: pass
                        except:
                            if not(str(quadro[turma][p[0]][turno][p[1]].teacher.schedule[p[0]][turno][p[1]]).split('-')[-1] in str(quadro[turma][p[0]][turno][p[1]])):
                                print('606, depois de recolocar')
                                break
                            else:
                                try:
                                    if not(str(quadro[turma][p[3]][turno][p[4]].teacher.schedule[p[3]][turno][p[4]]).split('-')[-1] in str(quadro[turma][p[3]][turno][p[4]])):
                                        print('606, depois de recolocar')
                                        break
                                except: pass
                    """
                if not(TESTE_passou_pela_reposition) and not(TESTE_passou_pela_troca):
                    print('XXXXXXXXXXXXX, O horário foi zerado e não colocamos outro no lugar.........')
                """
                for p in positions_for_horaries:
                
                    try:
                        if quadro[turma][p[0]][turno][p[1]][p[2]]:
                            if not(str(quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]]).split('-')[-1] in str(quadro[turma][p[0]][turno][p[1]][p[2]])):
                                print('MEIO', quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]], quadro[turma][p[0]][turno][p[1]][p[2]])
                                break
                        else:
                            try:
                                if not(str(quadro[turma][p[3]][turno][p[4]][p[5]].teacher.schedule[p[3]][turno][p[4]][p[5]]).split('-')[-1] in str(quadro[turma][p[3]][turno][p[4]][p[5]])):
                                    print('MEIO', quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]], quadro[turma][p[0]][turno][p[1]][p[2]])
                                    break
                            except: pass
                    except:
                        if not(str(quadro[turma][p[0]][turno][p[1]].teacher.schedule[p[0]][turno][p[1]]).split('-')[-1] in str(quadro[turma][p[0]][turno][p[1]])):
                            print('MEIO', quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]], quadro[turma][p[0]][turno][p[1]][p[2]])
                            break
                        else:
                            try:
                                if not(str(quadro[turma][p[3]][turno][p[4]].teacher.schedule[p[3]][turno][p[4]]).split('-')[-1] in str(quadro[turma][p[3]][turno][p[4]])):
                                    print('MEIO', quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]], quadro[turma][p[0]][turno][p[1]][p[2]])
                                    break
                            except: pass
                """
            else: # Vamos trocar dois normais de posição
                for p in positions_for_horaries:
                    if not(logic.valid_positions(quadro, turma, turno, p, positions_for_horaries)):
                        raise Exception('Apareceu um inválido')
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
                
                # Colocamos eles como sendo 0
                quadro[turma][dia_1][turno][p_1] = 0
                quadro[turma][dia_2][turno][p_2] = 0
                horario_1.teacher.schedule[dia_1][turno][p_1] = 0
                try: horario_2.teacher.schedule[dia_2][turno][p_2] = 0
                except: pass # No caso de h2 ser 0
                
                # Vemos se é vaálido colocar eles naquela posição
                valid_1 = logic.validation(horario_1, (dia_2, p_2), quadro[turma], subjectPos_1,turno)
                if horario_2: valid_2 = logic.validation(horario_2, (dia_1, p_1), quadro[turma], subjectPos_2,turno)
                else: valid_2 = 0, 0 # Vai acontecer no caso em que for 0

                # Se for válidos realizamos a troca bem como alguns testes
                if not(valid_1[0]) and not(valid_2[0]): # Caso ambos sejam válidos
                    # Vamos trocar eles de lugar
                    """
                    for p in positions_for_horaries:
                        try:
                            if quadro[turma][p[0]][turno][p[1]][p[2]]:
                                if not(str(quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]]).split('-')[-1] in str(quadro[turma][p[0]][turno][p[1]][p[2]])):
                                    print('START', quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]], quadro[turma][p[0]][turno][p[1]][p[2]])
                                    break
                            else:
                                try:
                                    if not(str(quadro[turma][p[3]][turno][p[4]][p[5]].teacher.schedule[p[3]][turno][p[4]][p[5]]).split('-')[-1] in str(quadro[turma][p[3]][turno][p[4]][p[5]])):
                                        print('START', quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]], quadro[turma][p[0]][turno][p[1]][p[2]])
                                        break
                                except: pass
                        except:
                            if not(str(quadro[turma][p[0]][turno][p[1]].teacher.schedule[p[0]][turno][p[1]]).split('-')[-1] in str(quadro[turma][p[0]][turno][p[1]])):
                                print('START', quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]], quadro[turma][p[0]][turno][p[1]][p[2]])
                                break
                            else:
                                try:
                                    if not(str(quadro[turma][p[2]][turno][p[3]].teacher.schedule[p[2]][turno][p[3]]).split('-')[-1] in str(quadro[turma][p[2]][turno][p[3]])):
                                        print('START', quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]], quadro[turma][p[0]][turno][p[1]][p[2]])
                                        break
                                except: pass
                    """
                    logic.replace_h(quadro, turma, turno, horario_1, dia_1, p_1, horario_2, dia_2, p_2, positions_for_horaries)
                    
                    # Atualizamos a lista de posições, para que elas continuem indicando a mesma dupla de horários.
                    positions_for_horaries = logic.actualize_list_posittions(quadro,turma, turno, positions_for_horaries,
                                                                            dia_1, p_1, dia_2, p_2, horario_2)
                    for p in positions_for_horaries:
                        if not(logic.valid_positions(quadro, turma, turno, p, positions_for_horaries)):
                            raise Exception('Apareceu um inválido')
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
                    
                    # Vemos se a mudança é melhor do que o que já temos
                    value = logic.cost_board(quadro)
                    if value > better_board[1]:
                        # Salvando a melhor versão que temos até agora
                        better_board = (quadro.copy(), value, copy.deepcopy(teachers))
                        print('^^^', end='')
                        find_one_better = True

                    # Vemos se já é o bastante para colocar o novo_horario em algum lugar
                    if not(finishing):
                        position, motivo = logic.getBetterHour(novo_horario, quadro[novo_horario.turm[0]], subjectPos, typeNum)
                        if position != 'ERROR':
                            #print('passando por aqui 4')
                            print(turma, position)
                            return quadro, position
                        
                # Se não for válido recolocamos os antigos horários nas posições
                else:
                    quadro[turma][dia_1][turno][p_1] = horario_1
                    quadro[turma][dia_2][turno][p_2] = horario_2
                    horario_1.teacher.schedule[dia_1][turno][p_1] = horario_1
                    if horario_2: horario_2.teacher.schedule[dia_2][turno][p_2] = horario_2
                    else: pass # No caso de ser 0
            """
            for p in positions_for_horaries:
                try:
                    if quadro[turma][p[0]][turno][p[1]][p[2]]:
                        if not(str(quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]]).split('-')[-1] in str(quadro[turma][p[0]][turno][p[1]][p[2]])):
                            print('FINAL', quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]], quadro[turma][p[0]][turno][p[1]][p[2]])
                            break
                    else:
                        try:
                            if not(str(quadro[turma][p[3]][turno][p[4]][p[5]].teacher.schedule[p[3]][turno][p[4]][p[5]]).split('-')[-1] in str(quadro[turma][p[3]][turno][p[4]][p[5]])):
                                print('FINAL', quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]], quadro[turma][p[0]][turno][p[1]][p[2]])
                                break
                        except: pass
                except:
                    if not(str(quadro[turma][p[0]][turno][p[1]].teacher.schedule[p[0]][turno][p[1]]).split('-')[-1] in str(quadro[turma][p[0]][turno][p[1]])):
                        print('FINAL', quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]], quadro[turma][p[0]][turno][p[1]][p[2]])
                        break
                    else:
                        try:
                            if not(str(quadro[turma][p[3]][turno][p[4]].teacher.schedule[p[3]][turno][p[4]]).split('-')[-1] in str(quadro[turma][p[3]][turno][p[4]])):
                                print('FINAL', quadro[turma][p[0]][turno][p[1]][p[2]].teacher.schedule[p[0]][turno][p[1]][p[2]], quadro[turma][p[0]][turno][p[1]][p[2]])
                                break
                        except: pass
            """    

            # =============================================================================================
            # ==================================ANTIGO CÓDIGO A FRENTE=====================================
            # =============================================================================================
            """
            if not(horario_1): # Esse horário não pode estar vazio
                time -= 1
                #print('voltou (1)', end='')
                continue
            if quadro[turma][dia_1][turno][p_1] == 0:
                print('448, vendo se h1 realmente é diferente de 0', quadro[turma][dia_1][turno], p_1)

            # Se for uma lista, selecionamos um horário específico dentre os bimestrais
            if type(horario_1) is list:
                passed = False
                not_checked = [c for c in range(0, len(horario_1)-1)]

                for c_bimestral in range(0, 4):
                    pb_1 =  random.choice(not_checked)
                    not_checked.remove(pb_1)
                    
                    if len(horario_1) <= pb_1:
                        print('pb_1 está maior do que devia: ', quadro[turma][dia_1][turno], p_1, pb_1)

                    if horario_1[pb_1] != 0: # Ele também não pode ser 0
                        h_bimestral_1 = horario_1[pb_1]
                        passed = True
                        break
                    if len(not_checked) == 0:
                        break

                if not(passed): # Se não achou nenhum a gente escolhe outro 
                    continue
                already_changed = []
                for c in range(0, 50):  # Número arbitrário de repetições para achar um horário válido
                    print('_', end='')
                    # Selecionamos o segundo horário

                    #dia_2 = random.choice(list(quadro[turma].keys()))
                    dia_2 = random.choice(days_zero)
                    p_2 = random.randint(0, len(quadro[turma][dia_2][turno])-1)
                    horario_2 = quadro[turma][dia_2][turno][p_2]
                    

                    # Se os horários forem de mesmo tipo poderemos trocar os dois de lugar
                    if type(horario_2) is list:
                        pb_2 = random.randint(0, len(horario_2)-1)

                        # Verificamos se os mesmos horários já não haviam mudado de posição antes
                        if (dia_1, dia_2, p_1, p_2) in already_changed:
                            c -= 0.5
                            continue
                        already_changed.append((dia_1, dia_2, p_1, p_2, pb_1, pb_2))

                        h_bimestral_2 = horario_2[pb_2]
                        if len(horario_1) != len(horario_2) or (h_bimestral_1.type != h_bimestral_2): # Eles são de tipos diferentes
                            continue
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

                            if h_bimestral_1.teacher.schedule[dia_1][turno][p_1] == 0:
                                print('479 bimestral', h_bimestral_1.teacher.schedule[dia_1][turno][p_1], pb_1)

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
                                    logic.replace_h(quadro, turma, turno, h_bimestral_1, dia_1, p_1, h_bimestral_2, dia_2, p_2, pb_1=pb_1, pb_2=pb_2)
                                    #print(time, end='')
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
                            if value > better_board[1]:
                                teachers_version = copy.deepcopy(teachers)
                                better_board = (quadro, value, teachers_version)
                                print('^', end='')
                                find_one_better = True
                            
                            break
                        else: # Os horarios são de tipos diferentes
                            time -= 1
                            #print('voltou (2)', end='')
                            continue
                    elif not(horario_2) and (type(quadro[turma][dia_1][turno][p_1]) is list):
                        # Se o segundo horário for 0, não precisamos fazer algumas coisas nele
                        subjectPos_1 = h_bimestral_1.teacher.subjects.index(f"{h_bimestral_1.subject}") 
                        try:
                            h_bimestral_1.teacher.schedule[dia_1][turno][p_1][pb_1] = 0
                        except:
                            print('Não achou', h_bimestral_1.teacher.schedule[dia_1][turno], p_1, pb_1)
                        # Colocamos os valores como sendo 0, para que na hora de validar não apareça como já tendo um horário naquele lugar.
                        quadro[turma][dia_1][turno][p_1][pb_1] = 0
                        h_bimestral_1.teacher.schedule[dia_1][turno][p_1][pb_1] = 0
                        pb_2 = random.randint(0, len(horario_1)-1)

                        # Verificamos se esse horário já não foi testado antes
                        if (dia_1, dia_2, p_1, p_2) in already_changed:
                            c -= 0.25
                            continue
                        already_changed.append((dia_1, dia_2, p_1, p_2, pb_1, pb_2))

                        valid_1 = logic.validation(h_bimestral_1, (dia_2, p_2, pb_2), quadro[turma], subjectPos_1,turno, 1)
                        if valid_1[0] == 0:
                            # Criamos a lista nessa posição
                            logic.replace_h(quadro, turma, turno, h_bimestral_1, dia_1, p_1, 0, dia_2, p_2, pb_1, pb_2)
                        else:
                            quadro[turma][dia_1][turno][p_1][pb_1] = h_bimestral_1
                            h_bimestral_1.teacher.schedule[dia_1][turno][p_1][pb_1] = h_bimestral_1
                            # Se não tiver mais nenhum bimestral na lista, podemos apenas remover ela
                            if quadro[turma][dia_1][turno][p_1].count(0) == len(quadro[turma][dia_1][turno][p_1]):
                                quadro[turma][dia_1][turno][p_1] = 0
                            if len(h_bimestral_1.teacher.schedule[dia_1][turno][p_1]) == h_bimestral_1.teacher.schedule[dia_1][turno][p_1].count(0):
                                #print('lista a ser removida: ', h_bimestral_1.teacher.schedule[dia_1][turno][p_1])
                                h_bimestral_1.teacher.schedule[dia_1][turno][p_1] = 0
                            



            elif not(type(quadro[turma][dia_1][turno][p_1]) is list): # Horários normais
                already_changed = []
                for c in range(0, 50):  # Número arbitrário de repetições para achar um horário válido
                    print('_', end='')
                    # Selecionamos o segundo horário
                    #dia_2 = random.choice(list(quadro[turma].keys()))
                    dia_2 = random.choice(days_zero)
                    p_2 = random.randint(0, len(quadro[turma][dia_2][turno])-1)
                    horario_2 = quadro[turma][dia_2][turno][p_2]
                    if (dia_1, dia_2, p_1, p_2) in already_changed:
                        c -= 0.25
                        continue
                    already_changed.append((dia_1, dia_2, p_1, p_2))
                    
                    if type(horario_2) is list:
                        continue
                    

                    # Se os horários forem de mesmo tipo poderemos trocar os dois de lugar
                    if not(horario_2) or (type(horario_1) == type(horario_2)): # IF INÚTIL?
                        # Vemos se é válido trocar os dois horários de posição
                        subjectPos_1 = horario_1.teacher.subjects.index(f"{horario_1.subject}")
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
                                #print(time, end='')
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
                        if value > better_board[1]:
                            teachers_version = copy.deepcopy(teachers)
                            better_board = (quadro, value, teachers_version)
                            print('^', end='')
                            find_one_better = True
                            
        if finishing:
            if not(find_one_better):
                logic.actualize(teachers, better_board[2])
                #print('passando por aqui 2')
                return better_board[0], 0
        else:
            print('LIMITE', times - (LIMITE + int(better_board[1] / 100)))
            if find_one_better:
                logic.print_quadro(quadro, novo_horario, typeNum)
            if times == LIMITE + int(better_board[1] / 100):
                #print('passando por aqui 1')
                return 'Não conseguiu achar um melhor', 0
            
    #print('passando pelo final')
    logic.actualize(teachers, better_board[2])  
    return better_board[0], 0
    """

from functions import loadData
from functions import classes as c
from functions import result
from functions import logic
import random
import copy

NUMERO_DE_REPETIÇÕES = 1
NUMERO_DE_REPETIÇÕES_OP = 100
LIMITE = 20

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



                #if not('ELM-2NA' in horario.turm[0]):
                    #continue



                subjectPos = horario.teacher.subjects.index(f"{horario.subject}")  # -{horario.turm[0].split('-')[1]}")
               
                typeV = horario.teacher.types[subjectPos]
                typeNum = 0
                if typeV == 'Tarde': typeNum = 1
                elif typeV == 'Noite': typeNum = 2
                # Seleciono qual o melhor estado para aquele horário
                #print('==========================')
                #logic.print_quadro(quadro, horario, typeNum)
                position, motivo = logic.getBetterHour(horario, quadro.copy()[horario.turm[0]], subjectPos,
                                                typeNum)  # type é 0 - manha ou 1 - tarde. retorna 'day;hour;turm;room' 
                if position == 'ERROR':
                    #raise Exception('Parou')
                    print('Optimizando...', end='')
                    new_board, position = Optmizer(quadro,teachers, horario, subjectPos, typeNum, motivo=motivo)
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
        print('Finalizando...')
        quadro = Optmizer(quadro, teachers, finishing=True)
        break

    horarios = random.choice(bestSchedule)

    for turm in classes:
        result.saveSheet(turm.name, horarios[0][turm.name], type='turm')
    for teacher in teachers:
        result.saveSheet(teacher.name, horarios[2][teachersNames.index(teacher.name)].schedule, type='teacher')


def Optmizer(quadro_base, teachers, novo_horario=None, subjectPos=0, typeNum=0, finishing=False, motivo=''):
    """
    finishing => Essa função poder ser usada para organizar os horários durante a criação,
                 de modo que quando o horário que não possuia lugar já possuir um lugar para ser colocado, nós retornamos e paramos o código
                 Seu segundo uso é para quando já terminamos de organizar o quadro, e portanto podemos apenas usar a função para melhorar o resultado final.
    """
    # Primeiramente, vamos ver se não tem nada de errado nas informações que estamos recebendo.
    already_check = []
    times = 0
    print(f'{motivo}')
    if not(finishing): 
        logic.print_quadro(quadro_base, novo_horario, typeNum)

    # Inicialmos com uma grade horária funcional
    quadro = quadro_base.copy()
    if finishing:
        better_board = (logic.save_board(quadro), logic.cost_board(quadro_base), copy.deepcopy(teachers))
    else:
        better_board = (logic.save_board(quadro), logic.cost_board(quadro_base, in_optimizer=True, novo_horario=novo_horario), copy.deepcopy(teachers))
    find_one_better = False
    lista_com_trocas_feitas = []


    # Começamos a organizá-la
    while True:
        print('\n')
        if not(finishing):
            if '0' in novo_horario.type: print('    NORMAL', end=' ')
            else: print(f'   BIMESTRAL', end=' ')
        
        if find_one_better: times = 0
        elif times == 30 and finishing: return better_board[0]

        times += 1
        
        # Criamos a cópia do quadro, continuamos atualizando o melhor estado
        quadro = logic.save_board(better_board[0])
        logic.actualize(teachers, better_board[2])

        turma, positions_for_horaries = logic.select_turm_and_positions_list(finishing, novo_horario, quadro, typeNum, just_zeros=not(finishing))
        print(turma, end='')
        turno = typeNum
        if find_one_better:
            lista_com_trocas_feitas.append(trocas)
            if not(finishing): 
                logic.print_quadro(better_board[0], novo_horario, turno)
                #logic.TESTANDO_POSITIONS(better_board[0], novo_horario.turm[0], typeNum, subjectPos, novo_horario)

            find_one_better = False

        #logic.remove_already_check_positions(positions_for_horaries, already_check, 4)
        trocas = 0

        v = 10 if finishing else 1
        #int((5-v) + len(positions_for_horaries) // (30*v))
        for time in range(1, 11): # vezes que vamos realizar a mudança em um horário
            print(f'_', end='')
            # Se a lista estiver vazia, não tem como passar pelo código
            if len(positions_for_horaries) == 0:
                break
            
            logic.TESTANDO_erros(quadro, turma, turno, positions_for_horaries)
            
            turno = typeNum

            pesos = logic.get_weights(positions_for_horaries, quadro, turma, turno, novo_horario, finishing)
            
            # Escolhemos duas posições aleatórias dessa turma
            random_one = random.choices(positions_for_horaries, weights=pesos)[0]

            # Removemos ele para não adicionarmos ele novamente
            positions_for_horaries.remove(random_one)
            if not(logic.valid_positions(quadro, turma, turno, random_one, positions_for_horaries)):
                raise Exception('Random_one está errado')
            # Adicionamos elas a lista de posições que já realizamos a troca.
            already_check.append(random_one)
            
            #logic.TESTANDO_erros(quadro, turma, turno, positions_for_horaries)
            
            if random_one in positions_for_horaries:
                print('Ainda está aqui!!!, ', positions_for_horaries.count(random_one))
            # Selecionamos o horário que corresponde a essa posição específica
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
            

            #logic.TESTANDO_erros(quadro, turma, turno, positions_for_horaries)
            if len(random_one) == 6: # Vamos trocar dois bimestrais de posição
                
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
                    trocas += 1
                    # Vamos trocar eles de lugar
                    logic.replace_h(quadro, turma, turno, h_bimestral_1, dia_1, p_1, h_bimestral_2, dia_2, p_2,positions_for_horaries, pb_1=pb_1, pb_2=pb_2)

                    positions_for_horaries = logic.actualize_list_posittions(quadro,turma, turno, positions_for_horaries,
                                                                            dia_1, p_1, dia_2, p_2, pb1=pb_1, pb2=pb_2)
                    logic.TESTANDO_erros(quadro, turma, turno, positions_for_horaries)
                    # Vemos se é melhor do que o que já temos
                    if finishing: value = logic.cost_board(quadro)
                    else:         value = logic.cost_board(quadro, in_optimizer=True, novo_horario=novo_horario, typeNum=typeNum)

                    if value > better_board[1]:
                        # Quero manter uma cópia salvae que não varie conforme mudamos as váriáveis tentando achar uma melhor
                        better_board = (logic.save_board(quadro), value, copy.deepcopy(teachers))
                        print('^^^', end='')
                        find_one_better = True
                        break

                    logic.TESTANDO_erros(quadro, turma, turno, positions_for_horaries)

                    # Vemos se já é o bastante para colocar o novo_horario em algum lugar
                    if not(finishing):
                        position, motivo = logic.getBetterHour(novo_horario, quadro[novo_horario.turm[0]], subjectPos, typeNum)
                        if position != 'ERROR':
                            #print('passando por aqui 4')
                            print(turma, position)
                            lista_com_trocas_feitas.append(trocas)
                            total = 0
                            for t in lista_com_trocas_feitas:
                                total += t
                            print('TOTAL -> ', total/len(lista_com_trocas_feitas))
                            return quadro, position
                else: # Se não for válido deixamos de novo do jeito que era
                    time -= 1
                    quadro[turma][dia_1][turno][p_1][pb_1] = h_bimestral_1
                    h_bimestral_1.teacher.schedule[dia_1][turno][p_1][pb_1] = f"{h_bimestral_1.turm[0]}-{str(h_bimestral_1).split('-')[1]}"
                    
                    if quadro[turma][dia_2][turno][p_2]:
                        if h_bimestral_2:
                            quadro[turma][dia_2][turno][p_2][pb_2] = h_bimestral_2
                            h_bimestral_2.teacher.schedule[dia_2][turno][p_2][pb_2] = f"{h_bimestral_2.turm[0]}-{str(h_bimestral_2).split('-')[1]}"
                    logic.TESTANDO_erros(quadro, turma, turno, positions_for_horaries)
                
            else: # Vamos trocar dois normais de posição
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
                    logic.replace_h(quadro, turma, turno, horario_1, dia_1, p_1, horario_2, dia_2, p_2, positions_for_horaries)
                    
                    # Atualizamos a lista de posições, para que elas continuem indicando a mesma dupla de horários.
                    positions_for_horaries = logic.actualize_list_posittions(quadro,turma, turno, positions_for_horaries,
                                                                            dia_1, p_1, dia_2, p_2, horario_2)

                    logic.TESTANDO_erros(quadro, turma, turno, positions_for_horaries)
                
                    # Vemos se a mudança é melhor do que o que já temos
                    if finishing:
                        value = logic.cost_board(quadro)
                    else:    
                        value = logic.cost_board(quadro, in_optimizer=True, novo_horario=novo_horario, typeNum=typeNum)
                    if value > better_board[1]:
                        # Salvando a melhor versão que temos até agora
                        better_board = (quadro.copy(), value, copy.deepcopy(teachers))
                        print('^^^', end='')
                        find_one_better = True
                        break

                    # Vemos se já é o bastante para colocar o novo_horario em algum lugar
                    if not(finishing):
                        position, motivo = logic.getBetterHour(novo_horario, quadro[novo_horario.turm[0]], subjectPos, typeNum)
                        if position != 'ERROR':
                            lista_com_trocas_feitas.append(trocas)
                            total = 0
                            for t in lista_com_trocas_feitas:
                                total += t
                            print(total/len(lista_com_trocas_feitas))
                            print(turma, position)
                            return quadro, position
                        
                # Se não for válido recolocamos os antigos horários nas posições
                else:
                    time -= 1
                    quadro[turma][dia_1][turno][p_1] = horario_1
                    quadro[turma][dia_2][turno][p_2] = horario_2
                    horario_1.teacher.schedule[dia_1][turno][p_1] = horario_1
                    if horario_2: horario_2.teacher.schedule[dia_2][turno][p_2] = horario_2
                    else: pass # No caso de ser 0  

            #logic.TESTANDO_erros(quadro, turma, turno, positions_for_horaries)
        logic.TESTANDO_erros(quadro, turma, turno, positions_for_horaries)
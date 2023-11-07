from functions import loadData
from functions import classes as c
from functions import result
from functions import logic
import random
import copy

NUMERO_DE_REPETIÇÕES = 1
NUMERO_DE_REPETIÇÕES_OP = 50
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
    teachers, teachersNames, classes, teachersData = organizing_data()

    # ==================== Processando os dados: Gerando a planilha final com base nos dados
    print('verificando', end =' ')
    verificador_professores(teachers)
    verificando_turmas(classes, teachers)
    print('ok')
    bestSchedule = []
    # Duplicar os objetos professores e manipular apenas umgrupo nessa parte a baixo
    for time in range(0, NUMERO_DE_REPETIÇÕES): # Por emquanto estamos nos focando em fazer apenas uma repetição
        print('.', end=' ')
        ERRO_NOS_HORARIOS = False
        teachers_copy = restartObjects(teachers)

        # Embaralha a lista de professores
        lista_embaralhada = teachers.copy()
        random.shuffle(lista_embaralhada)

        # Quadro de horários em branco
        quadro = {}
        quadro_de_horarios_em_branco(quadro, classes)
       
        while len(lista_embaralhada) != 0:
            # Retiro o primeiro item da lista e o coloco na variável teacher
            teacher = lista_embaralhada[0]
            lista_embaralhada = lista_embaralhada[1:]

            # lista com os objetos horários do professores
            h_professor = teacher.h_individuais

            for horario in h_professor:

                
                if ('NA' in horario.turm[0] or 'NB' in horario.turm[0]):
                    continue

                subjectPos = horario.teacher.subjects.index(f"{horario.subject}")  # -{horario.turm[0].split('-')[1]}")
                typeV = horario.teacher.types[subjectPos]
                
                typeNum = 0
                if typeV == 'Tarde':   typeNum = 1
                elif typeV == 'Noite': typeNum = 2

                # Seleciono qual o melhor estado para aquele horário
                position, motivo = logic.getBetterHour(horario, quadro.copy()[horario.turm[0]], subjectPos,
                                                typeNum)  # type é 0 - manha ou 1 - tarde. retorna 'day;hour;turm;room' 
                if position == 'ERROR':
                    
                    print('Optimizando...', end='')
                    new_board, position = Optmizer(quadro,teachers, horario, subjectPos, typeNum, motivo=motivo)
                    
                    # Se isso aqui passar, quer dizer que a função não retornou nada porque aconteceu um erro, ela está começando de novo.
                    if new_board == None and position == None:
                        break
                    
                    print('.')
                    print('achou!')
                    if new_board == 'Não conseguiu achar um melhor':
                        ERRO_NOS_HORARIOS = True
                        break
                    else:
                        quadro = new_board

                position_info = position.split(';')

                # Coloco o horário naquela posição
                put_h_in_the_place(quadro, horario, position_info, typeNum, teacher, teachers_copy, teachersNames, subjectPos)
                

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

        print(time, 'Resultado', int(pontuacao))
        print('Finalizando...')

        quadro = Optmizer(quadro, teachers, finishing=True)
        print('Nova pontuação final: ', logic.cost_board(quadro))
        break
    verificar_se_esta_completo(teachers, teachersData)
    
    horarios = random.choice(bestSchedule)
    # Dando tudo certo, vamos salvar as informações nas tabelas.
    
    for turm in classes:
        result.saveSheet(turm.name, horarios[0][turm.name], tipo='turm')
    for teacher in teachers:
        result.saveSheet(teacher.name, horarios[2][teachersNames.index(teacher.name)].schedule, tipo='teacher')


def Optmizer(quadro_base, teachers, novo_horario=None, subjectPos=0, typeNum=0, finishing=False, motivo='', NUMERO_DE_REPETIÇÕES_OP=NUMERO_DE_REPETIÇÕES_OP):
    """
    finishing => Essa função poder ser usada para organizar os horários durante a criação,
                 de modo que quando o horário que não possuia lugar já possuir um lugar para ser colocado, nós retornamos e paramos o código
                 Seu segundo uso é para quando já terminamos de organizar o quadro, e portanto podemos apenas usar a função para melhorar o resultado final.
    """
    # Primeiramente, vamos ver se não tem nada de errado nas informações que estamos recebendo.
    already_check = []
    times = 0
    times_of_optimizing = 0
    weights_list = 0
    print(f'{motivo}')
    if not(finishing): 
        logic.print_quadro(quadro_base, novo_horario, typeNum)
        

    # Inicialmos com uma grade horária funcional
    quadro = quadro_base.copy()
    if finishing: better_board = (logic.save_board(quadro), logic.cost_board(quadro_base), copy.deepcopy(teachers))
    else:         better_board = (logic.save_board(quadro), logic.cost_board(quadro_base, in_optimizer=True, novo_horario=novo_horario), copy.deepcopy(teachers))
    find_one_better = False
    find_better_in_this_turm = 0
    reset = False

    # Começamos a organizá-la
    while True:
        
        if finishing: print('.')
        print('\n')
        print(times_of_optimizing, end=' ')
        times_of_optimizing += 1
        if not(finishing):
            if '0' in novo_horario.type: print('    NORMAL', end=' ')
            else:                        print('    BIMESTRAL', end=' ')
        
        # É aqui que decidimos a hora de parar o código caso não ache um resultado, ou esteja apenas finalizando
        if find_one_better: times = 0
        elif times == NUMERO_DE_REPETIÇÕES_OP and finishing: return better_board[0] # Quando está apenas finalizando
        elif times == 50:   
            reset = True
            break
        times += 1
        
        # Criamos a cópia do quadro, continuamos atualizando o melhor estado
        quadro = logic.save_board(better_board[0])
        logic.actualize(teachers, better_board[2])
        
        turma, positions_for_horaries, weights_list = logic.select_turm_and_positions_list(finishing, novo_horario, quadro, typeNum, just_zeros=not(finishing), teachers=teachers, last_turm=find_better_in_this_turm, last_weights=weights_list)
        find_better_in_this_turm = 0
        print(turma, end='')

        turno = typeNum

        if find_one_better and not(finishing): 
            logic.print_quadro(better_board[0], novo_horario, turno)
            #logic.TESTANDO_POSITIONS(quadro, novo_horario.turm[0], typeNum, subjectPos=subjectPos, horario=novo_horario)
        find_one_better = False

        #logic.remove_already_check_positions(positions_for_horaries, already_check, 4)

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
                horario_2 = quadro[turma][dia_2][turno][p_2]
                subjectPos_1 = horario_1.teacher.subjects.index(f"{horario_1.subject}")
                
                try: subjectPos_2 = horario_2.teacher.subjects.index(f"{horario_2.subject}")
                except: pass # Vai acontecer quando for 0
            

            #logic.TESTANDO_erros(quadro, turma, turno, positions_for_horaries)
            if len(random_one) == 6: # Vamos trocar dois bimestrais de posição
                
                # Fazemos os dois serem 0, necessário para passar pelo validation
                put_0_in_position(quadro, turma, turno, dia_1, p_1, dia_2, p_2, pb_1=pb_1, pb_2=pb_2, h_bimestral_1=h_bimestral_1, h_bimestral_2=h_bimestral_2)
                    
                # Vemos se a mudança de posição é valida
                valid_1 = logic.validation(h_bimestral_1, (dia_2, p_2, pb_2), quadro[turma], subjectPos_1,turno, 1)
                try: valid_2 = logic.validation(h_bimestral_2, (dia_1, p_1, pb_1), quadro[turma], subjectPos_2,turno, 1)
                except: valid_2 = 0, 0 # Vai acontecer no caso em que for 0
                
                # Se for válida trocamos os dois de posição
                if not(valid_1[0]) and not(valid_2[0]): # Caso ambos sejam válidos
                    # Vamos trocar eles de lugar
                    logic.replace_h(quadro, turma, turno, h_bimestral_1, dia_1, p_1, h_bimestral_2, dia_2, p_2,positions_for_horaries, pb_1=pb_1, pb_2=pb_2)

                    positions_for_horaries = logic.actualize_list_posittions(quadro,turma, turno, positions_for_horaries,
                                                                            dia_1, p_1, dia_2, p_2, pb1=pb_1, pb2=pb_2)
                    logic.TESTANDO_erros(quadro, turma, turno, positions_for_horaries)
                    # Vemos se é melhor do que o que já temos
                    if finishing: value = logic.cost_board(quadro)
                    else:         value = logic.cost_board(quadro, in_optimizer=True, novo_horario=novo_horario, typeNum=typeNum)
                    
                    # Se o quadro do professor estiver diferente, vamos pontuar esse estado
                    i = 0
                    if not finishing:
                        for teacher in better_board[2]:
                            if teacher.name == novo_horario.teacher.name:
                                if teacher.schedule != novo_horario.teacher.schedule:
                                    i = 20
                    if value + i > better_board[1]:
                        # Quero manter uma cópia salvae que não varie conforme mudamos as váriáveis tentando achar uma melhor
                        better_board = (logic.save_board(quadro), value, copy.deepcopy(teachers))
                        print('^^^', end='')
                        find_one_better = True
                        find_better_in_this_turm = turma
                        break

                    logic.TESTANDO_erros(quadro, turma, turno, positions_for_horaries)

                    # Vemos se já é o bastante para colocar o novo_horario em algum lugar
                    if not(finishing):
                        position, motivo = logic.getBetterHour(novo_horario, quadro[novo_horario.turm[0]], subjectPos, typeNum)
                        if position != 'ERROR': return quadro, position
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
                put_0_in_position(quadro, turma, turno, dia_1, p_1, dia_2, p_2, horario_1=horario_1, horario_2=horario_2)
                
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
                    # Se o quadro do professor estiver diferente, vamos pontuar esse estado
                    i = 0
                    if not finishing:
                        for teacher in better_board[2]:
                            if teacher.name == novo_horario.teacher.name:
                                if teacher.schedule != novo_horario.teacher.schedule:
                                    i = 20
                    if value + i > better_board[1]:
                        # Salvando a melhor versão que temos até agora
                        better_board = (quadro.copy(), value, copy.deepcopy(teachers))
                        print('^^^', end='')
                        find_one_better = True
                        find_better_in_this_turm = turma
                        break

                    # Vemos se já é o bastante para colocar o novo_horario em algum lugar
                    if not(finishing):
                        position, motivo = logic.getBetterHour(novo_horario, quadro[novo_horario.turm[0]], subjectPos, typeNum)
                        if position != 'ERROR': return quadro, position
                        
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


    if reset:
        print(' ')
        print('Recomeçando de novo ...')
        
        try:
            mainFunction()
        except: pass
        #return None, None
        # Depois que chamamos o main function ele realiza todas as operações novamente. Mas com o código já tendo terminado.
        # Ele não pode fazer mais nenhuma operação depois que passa daqui.



def criar_as_salas(planilha):
    turmas = []
    objetos_turmas = []

    for i in range(0, len(list(planilha.values())[0])):
        for d in list(planilha.keys())[12:]:
            if planilha[d][i] != 0:
                if not((f"{d}-{str(planilha['Ano'][i])}{planilha['Sub-Grupo'][i]}") in turmas):
                    objetos_turmas.append(c.Turm(d, planilha['Ano'][i], planilha['Sub-Grupo'][i]))
                    turmas.append(f"{d}-{str(planilha['Ano'][i])}{planilha['Sub-Grupo'][i]}")
    print(turmas)
    return objetos_turmas

def put_0_in_position(quadro, turma, turno, dia_1, p_1, dia_2, p_2, pb_1=None, pb_2=None, h_bimestral_1=None, h_bimestral_2=None, horario_1=None, horario_2=None):
    if pb_1 != None:

        if len(quadro[turma][dia_1][turno][p_1]) == 4 and h_bimestral_1.type[2] == 2:
            for b in range(0, 4): # Pra que isso?
                if quadro[turma][dia_1][turno][p_1][b].subject == h_bimestral_1.subject: quadro[turma][dia_1][turno][p_1][b] = 0
        if h_bimestral_2:
            if len(quadro[turma][dia_2][turno][p_2]) == 4 and h_bimestral_2.type[2] == 2:
                for b in range(0, 4):
                    if quadro[turma][dia_2][turno][p_2][b].subject == h_bimestral_1.subject: quadro[turma][dia_2][turno][p_1][b] = 0


        quadro[turma][dia_1][turno][p_1][pb_1] = 0
        if h_bimestral_1.coteacher: h_bimestral_1.coteacher.schedule[dia_1][turno][p_1][pb_1] = 0
        h_bimestral_1.teacher.schedule[dia_1][turno][p_1][pb_1] = 0
        if quadro[turma][dia_2][turno][p_2]:
            if h_bimestral_2 != 0:
                h_bimestral_2.teacher.schedule[dia_2][turno][p_2][pb_2] = 0
                if h_bimestral_2.coteacher: h_bimestral_2.coteacher.schedule[dia_2][turno][p_2][pb_2] = 0
                quadro[turma][dia_2][turno][p_2][pb_2] = 0
    else:
        quadro[turma][dia_1][turno][p_1] = 0
        quadro[turma][dia_2][turno][p_2] = 0
        horario_1.teacher.schedule[dia_1][turno][p_1] = 0
        try: horario_2.teacher.schedule[dia_2][turno][p_2] = 0
        except: pass # No caso de h2 ser 0

def quadro_de_horarios_em_branco(quadro, classes):
    for turm in classes:
            quadro[turm.name] = {
                '2': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],  # manhã e tarde
                '3': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
                '4': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
                '5': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
                '6': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]]
            }


def verificador_professores(teachers):
    """
    vamos verificar se os dados dos professores são válidos, se é possível que criemos uma planilha com aqueles horários
    """
    n_de_aulas = {}
    for t in teachers:
        n_de_aulas[t.name] = [0, 0, 0]
        for horario in t.h_individuais:
            
            subjectPos = horario.teacher.subjects.index(f"{horario.subject}")  # -{horario.turm[0].split('-')[1]}")
            typeV = horario.teacher.types[subjectPos]

            if typeV == 'Tarde':
                if horario.type[0] == '1':
                    
                    if '0' in horario.type:
                        n_de_aulas[t.name][1] += 1
                    elif horario.type[2] == '1':
                        n_de_aulas[t.name][1] += 0.25
                    elif '4,G' in horario.type:
                        n_de_aulas[t.name][1] += 1/3
                    else:
                        n_de_aulas[t.name][1] += 0.5
                else:
                    n_de_aulas[t.name][1] += 1
                

            elif typeV == 'Noite':
                if horario.type[0] == '1':
                    if '0' in horario.type:
                        n_de_aulas[t.name][2] += 1
                    elif horario.type[2] == '1':
                        n_de_aulas[t.name][2] += 0.25
                    elif '4,G' in horario.type:
                        n_de_aulas[t.name][2] += 1/3
                    else:
                        n_de_aulas[t.name][2] += 0.5
                else:
                    n_de_aulas[t.name][2] += 1
            else:
                if horario.type[0] == '1':
                    if '0' in horario.type:
                        n_de_aulas[t.name][0] += 1
                    elif horario.type[2] == '1':
                        n_de_aulas[t.name][0] += 0.25
                    elif '4,G' in horario.type:
                        n_de_aulas[t.name][0] += 1/3
                    else:
                        n_de_aulas[t.name][0] += 0.5
                else:
                    n_de_aulas[t.name][0] += 1
    
    for name, n in n_de_aulas.items():
        #if 'Guilherme' in name:
            #print('Guilherme', n)
        if n[0] > 30: raise Exception(f'O professor {name} não está com os horários adequados, ele está com uma carga horária de {n[0]} na parte da manhã, sendo o máximo 30')
        elif n[1] > 30: raise Exception(f'O professor {name} não está com os horários adequados, ele está com uma carga horária de {n[1]} na parte da tarde, sendo o máximo 30')
        elif n[2] > 20: raise Exception(f'O professor {name} não está com os horários adequados, ele está com uma carga horária de {n[2]} na parte da noite, sendo o máximo 20')
            
def verificando_turmas(classes, teachers):
    turmas = {}
    for turma in classes:
        turmas[turma.name] = 0
    for t in teachers:
        for h in t.h_individuais:
            if h.type == '0,0,0':
                turmas[h.turm[0]] += 1
            elif h.type[2] == '1':
                turmas[h.turm[0]] += 0.25
            else:
                turmas[h.turm[0]] += 0.5
    for turma, n in turmas.items():
        if turma[-2] == 'N' and n > 20:
            raise Exception(f'Horário da turma noturna {turma} está com {n} horários')
        elif n > 30:
            raise Exception(f'Horário da turma {turma} está com {n} horários')
    
def verificar_se_esta_completo(teachers, teachersData):
    """
    Vamos ver se os professores estão dando a quantidade de aulas que eles deveriam dar a princípio.
    """
    professores = {}
    
    for t in teachers:
        professores[t.name] = 0
        for day in t.schedule.values():
            for turno in range(0, 2):
                for h in day[turno]:
                    if type(h) is list:
                        for bimestral in h:
                            if bimestral: professores[t.name] += 1 #/len(h)
                    elif h: professores[t.name] += 1
                    
    for l in range(0, len(teachersData['Professor'])):
        if 'N' in teachersData['Sub-Grupo'][l]: # or ('B' == teachersData['Grupo'][l]):
            continue
        professores[teachersData['Professor'][l]] -= teachersData['MEC'][l] + teachersData['MCT'][l] + teachersData['ELM'][l]

    for k, v in professores.items():
        if v: print(f'{v} ---> {k}')
        
    

def organizing_data():
    """
    Recebemos as informações das planilhas que colocamos e etc e usamos elas para criar os objetos,
    Entre outras coisas que serão necessárias para o processamento.
    """
    
    try:
        teachersData = loadData.getDatabase('Planilha dos horários 2023.xlsx') ##  # Leitura inicial da planilha

        # A biblioteca substitui o NA por 0, assim, o seguinte código coloca de volta os nomes dos subgrupos que foram substituidos
        for i in range(0, len(teachersData['Sub-Grupo'])):
            if str(teachersData['Sub-Grupo'][i]) == '0':
                teachersData['Sub-Grupo'][i] = 'NA'
        teachersColumns = loadData.getDatabase('Planilha dos horários 2023.xlsx', get="columns") ##
        roomsData = loadData.getDatabase('Planilha sala.xlsx') # Leitura inicial da planilha de salas
        pointsData = loadData.getPoints('./data/preferencias.txt')  # Leitura das pontuações para o cost
    except Exception as e:
        print(f"Houve um erro ao tentar pegar os dados das planilhas.\n{e}")
    duplas_de_professores = loadData.get_coteacher_horaries(teachersData)
    # ==================== Processando os dados para deixa-los melhor de mexer

    classes = []  # Lista de objetos de cada turma
    
    classes = criar_as_salas(teachersData)
    teachersNames = []  # -- Professores
    teachers = []  # Lista de objetos de cada professor

    for index, teacher in enumerate(teachersData["Professor"]):  # Transforma cada professor em um objeto de uma classe
        horaries = {}  # Horários para cada turma e matéria
        for i in range(12, len(teachersColumns)):   # SE ACRESCENTAR OU TIRAR COLUNA NA TABELA, TEM QUE MUDAR O VALOR AQUI
            
            if teachersData[f"{teachersColumns[i]}"][index]:
            
                horaries[
                        f"{teachersColumns[i]}-" + f'{teachersData["Ano"][index]}' + f'{teachersData["Sub-Grupo"][index]}' + 
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
            teachersNames.append(teacher) #???
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
    tipos_para_duplas = {'2,1,G':'3,1,G'}
    for professor in teachers: 
        horarios = professor.horaries
        for i, h in enumerate(horarios.items()):
            materia = h[0]
            for turma in h[1].items():
                for time in range(0, turma[1]):
                    sala, tipo = turma[0].split('|')
                    # Esse if só está aqui porque não se sabe ainda como interpretar na tabela final como ficariam os horários de tipos diferentes.
                    if not(tipo in tipos_normais): #Os co professor não possuem horários do tipo normal. Temos que achar os dois passar o h de um para normal e excluir o outro
                        for dupla in duplas_de_professores[sala]:
                            if dupla[2] == materia:
                                if professor == dupla[0] or professor == dupla[1]:
                                    # Temos que passar o tipo de um dos professores para normal. Apenas de um deles.
                                    if tipo in tipos_para_duplas.keys():
                                        tipo = tipos_para_duplas[tipo]
                                        print('DUPLA -> ', dupla)
                                        duplas_de_professores[sala].remove(dupla)

                        pass
                    else:
                        ho = 0
                        if len(duplas_de_professores[sala]):
                            for dupla in duplas_de_professores[sala]:
                                if professor.name == 'Ismail' or professor.name == 'Vinicius':
                                    pass
                                if professor.name == dupla[0] and dupla[2] in materia:
                                    # Vamos achar o objeto do segundo professor:
                                    coteacher = find_second_teacher(teachers, dupla[1])
                                    ho = c.Horario(teacher=professor, coteacher=coteacher, subject=materia, turm=(sala, turma[1]), local=professor.locais[i], tipo=tipo)  # Objeto do horário
                                    professor.h_individuais.append(ho)
                                    break
                                elif professor.name == dupla[1] and dupla[2] in materia:
                                    coteacher = find_second_teacher(teachers, dupla[2])
                                    ho = c.Horario(teacher=professor, coteacher=coteacher, subject=materia, turm=(sala, turma[1]), local=professor.locais[i], tipo=tipo)  # Objeto do horário
                                    professor.h_individuais.append(ho)
                                    break
                        if not(ho):
                            ho = c.Horario(teacher=professor, subject=materia, turm=(sala, turma[1]), local=professor.locais[i], tipo=tipo)  # Objeto do horário
                            professor.h_individuais.append(ho)  # Uma lista com todos os objetos Horario do professor []

            professor.h_individuais = loadData.organize_table(professor.h_individuais)
    
    testing_teachers(teachers)
    roomsNames = roomsData['Sala'] # -- Salas
    rooms = []

    for index, room in enumerate(roomsNames):  # Transforma cada turma em um objeto de uma classe
        rooms.append(c.Room(room, roomsData['Local'][index], roomsData['Limitacoes'][index]))
    
    return teachers, teachersNames, classes, teachersData

def put_h_in_the_place(quadro, horario, position_info, typeNum, teacher, teachers_copy, teachersNames, subjectPos):
    """
    Temos um horário e colocamos ele em uma determinada posição no quadro.
    """
    #if type(quadro[position_info[3]][position_info[0]][typeNum][int(position_info[1])]) is list:
        #if len(quadro[position_info[3]][position_info[0]][typeNum][int(position_info[1])]) == 4 and horario.type[2] == '2': # É um caso especial
            #quadro[position]
            #pass
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
            raise Exception('Horário já ocupado')
        try: quadro[position_info[3]][position_info[0]][typeNum][int(position_info[1])][int(position_info[2])] = horario
        except:
            print('Posição inválida', position_info, typeNum)
            print(len(quadro[position_info[3]][position_info[0]][typeNum][int(position_info[1])]), horario, horario.type)
            print(quadro[position_info[3]][position_info[0]][typeNum])
            raise Exception('Horário Inválido')
        
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
            raise Exception('Erro na hora de colocar o horárion nos professores')
            print(horario.type, position_info[2], horario.teacher.schedule[position_info[0]][typeNum][int(position_info[1])], motivo)
        teachers_copy[teachersNames.index(horario.teacher.name)].schedule[position_info[0]][typeNum][
            int(position_info[1])] = list(horario.teacher.schedule[position_info[0]][typeNum][int(position_info[1])])
    else:
        horario.teacher.schedule[position_info[0]][typeNum][int(position_info[1])] = f"{horario.turm[0]}-{str(horario).split('-')[1]}"

        teachers_copy[teachersNames.index(horario.teacher.name)].schedule[position_info[0]][typeNum][
            int(position_info[1])] = f"{horario.turm[0]}-{str(horario).split('-')[1]}"
    # No caso do professor dividir a matéria com outro.
    if horario.coteacher:
        if '0' in horario.type:
            if not(type(horario.coteacher.schedule[position_info[0]][typeNum][int(position_info[1])]) is list): # Se no horário não for lista
            
                if '1' == horario.type[2]:
                    horario.coteacher.schedule[position_info[0]][typeNum][int(position_info[1])] = [0, 0, 0, 0]
                elif '4,G' in horario.type:
                    horario.coteacher.schedule[position_info[0]][typeNum][int(position_info[1])] = [0, 0, 0]
                elif '2,T' in horario.type or '4,T' in horario.type:
                    horario.coteacher.schedule[position_info[0]][typeNum][int(position_info[1])] = [0, 0]
            try:
                horario.coteacher.schedule[position_info[0]][typeNum][int(position_info[1])][int(position_info[2])] = f"{horario.turm[0]}-{str(horario).split('-')[1]}"
            except:
                raise Exception('Erro na hora de colocar o horárion nos professores', position_info, len(horario.coteacher.schedule[position_info[0]][typeNum][int(position_info[1])]))
            teachers_copy[teachersNames.index(horario.coteacher.name)].schedule[position_info[0]][typeNum][
                int(position_info[1])] = list(horario.coteacher.schedule[position_info[0]][typeNum][int(position_info[1])])
        else:
            horario.coteacher.schedule[position_info[0]][typeNum][int(position_info[1])] = f"{horario.turm[0]}-{str(horario).split('-')[1]}"

            teachers_copy[teachersNames.index(horario.coteacher.name)].schedule[position_info[0]][typeNum][
                int(position_info[1])] = f"{horario.turm[0]}-{str(horario).split('-')[1]}"


def testing_teachers(teachers):
    result = {}
    for teacher in teachers:
        result[teacher.name] = 0
    for teacher in teachers:
        for h in teacher.h_individuais:
            if h.coteacher: 
                result[teacher.name] += 1
                result[h.coteacher.name] += 1
    print('Teste dos coprofessores')
    for k, v in result.items():
        if v: print(f'{k}, {v}')
                
def find_second_teacher(teachers, name):
    for t in teachers:
        if t.name == name: return t





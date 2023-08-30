import pandas as pd
import numpy as np
import os
from functions import classes as c
#from classes import Node

def getDatabase(path, get="dict"): # Retorna um dicionário com os itens, como as colunas da planilha. E os valores como as linhas
    result = {}

    df = pd.read_excel(path) # Lê planilha
    df_columns = list(df.columns.values)
    df = df.fillna(0) # Preenche as celulas da planilha vazias, com 0.

    if get == "columns": # Lista das colunas
        return df_columns

    for col in df_columns:
        result[f"{col}"] = list(df[f"{col}"].values)

    return result

def getPoints(path, desc=False): # Retorna um dicionário com as pontuações
    with open(path) as file:
        text = file.readlines() # Lista das linhas do arquivo .txt
    soma = 0
    points = {}
    for line in text: # Salvando no dicionário
        if not desc:
            points[f"{line.split('=')[0]}"] = float(line.split(';')[0].split('=')[1])
            soma += float(line.split(';')[0].split('=')[1])
        else:
            points[f"{line.split('=')[0]}"] = str(line.split('//')[1]) # Descrição de cada
    
    for k in points.keys():
        points[k] = (points[k]/soma) * 10

    return points

def organize_table(board):
    """
    Esse código vai receber a planilha e organizá-la para que alguns dados sejam lidos,
    e portanto, colocados primeiro.
    Pretendemos coloca-los de uma forma que não gere conflito na hora que forem colocados:
    Horários não bimestrais primeiro, horários bimestrais ocupam espaço indefinido podendo estar juntos ou não.
    Horários no campus 2 primeiro, apenas algumas turmas tem aulas no c2, sendo as do c2 a minoria dos horários, colocálos primeiro facilita não dar erro.
    """
    """
    horarios_normais = []
    horarios_bimestrais = []
    h_b1 = []
    h_b2 = []
    h_b4 = []
    h_4G = []
    
    for h in board:
        if '0' in h.type and h.local == 'c2':
            horarios_normais.insert(0, (h))
        elif '0' in h.type:
            horarios_normais.append(h)
        elif h.local == 'c2' and '4,T' in h.type:
            h_b4.insert(0, h)
        elif '4,T' in h.type:
            h_b4.append(h)
        elif h.local == 'c2' and '2,T' in h.type:
            h_b2.insert(0, h)
        elif '2,T' in h.type:
            h_b2.append(h)
        elif h.local == 'c2' and '4,G' in h.type:
            h_4G.insert(0, h)
        elif '4,G' in h.type:
            h_4G.append(h)
        elif h.local == 'c2' and ('1,G' in h.type or '1,T' in h.type):
            h_b1.insert(0, h)
        elif '1,G' in h.type or '1,T' in h.type:
            h_b1.append(h)
        else:
            print('Errorrrrrrrrrrr', h, h.type)
    return horarios_normais + h_b4 + h_b2 + h_4G + h_b1
    """
    horarios_do_c1 = []
    normais_do_c1 = []
    horarios_do_c2 = []
    normais_do_c2 = []
    
    for h in board:
        if '1' in h.local:
            if '1' == h.type[2]: horarios_do_c1.insert(0, h)
            elif '0' in h.type: normais_do_c1.append(h)
            else: horarios_do_c1.append(h)
        else:
            if '1' == h.type[2]: horarios_do_c2.append(h)
            elif '0' in h.type: normais_do_c2.append(h)
            else: horarios_do_c2.insert(0, h)

    listas_juntas = horarios_do_c1 + normais_do_c1 + normais_do_c2 + horarios_do_c2

    resultado = []
    c = 0
    while len(listas_juntas) != 0:
        if c % 2 == 0:
            resultado.append(listas_juntas[0])
            listas_juntas = listas_juntas[1:]
        else:
            resultado.append(listas_juntas[-1])
            listas_juntas = listas_juntas[:-1]
        c += 1
    return resultado # [c1, c2, c1, c2, ...]

def organizando_dados_da_planilha():
    # =================== Pegando os dados que nós fornecemos
    try:
        teachersData = getDatabase('Planilha dos horários.xlsx') ##  # Leitura inicial da planilha
        # A biblioteca substitui o NA por 0, assim, o seguinte código coloca de volta os nomes dos subgrupos que foram substituidos
        for i in range(0, len(teachersData['Sub-Grupo'])):
            if str(teachersData['Sub-Grupo'][i]) == '0':
                teachersData['Sub-Grupo'][i] = 'NA'
        teachersColumns = getDatabase('Planilha dos horários.xlsx', get="columns") ##
        roomsData = getDatabase('Planilha sala.xlsx') # Leitura inicial da planilha de salas
        pointsData = getPoints('./data/preferencias.txt')  # Leitura das pontuações para o cost
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
                        print('tipo', tipo, professor, materia, sala, turma[1])
                    else:
                        ho = c.Horario(teacher=professor, subject=materia, turm=(sala, turma[1]), local=professor.locais[i], tipo=tipo)  # Objeto do horário
                        professor.h_individuais.append(ho)  # Uma lista com todos os objetos Horario do professor []
            #professor.h_individuais = loadData.organize_table(professor.h_individuais)

    return teachers, teachersNames
    
def get_functional_grade(path, teachers, teachersNames):
    """
    Vamos retornar uma grade de horários funcional, pode ser a que já está em uso
    """
    # Abrimos a pasta e pegamos lá dentro as planilhas com cada horário de cada sala.
    for turma in os.listdir(path):
        try:
            df = pd.read_excel(os.path.join(path, turma))
        except: continue
        print(turma)
        turma = turma.replace('.xlsx', '')
        # Vamos converter essa planilha para a forma que usamos no dicionário
        # {Turma:{dia_da_semana:[[manhã], [tarde], [noite]]}
        #print(df.columns)
        for c in range(1, len(df.columns)):
            dia = []
            discordancia = False
            for h in df[df.columns[c]]:
                if not(h in ['Janta', 'Intervalo', 'Almoço']):
                    if h == '-' or type(h) is float:
                        dia.append(0)
                    else:
                        if h[0] == '[':
                            bimestrais = []
                            h = h.replace('[', '')
                            h = h.replace(']', '')
                            h = h.split(', ')
                            for bimestral in h:
                                bimestral = bimestral.split('-')
                                if len(bimestral) != 2:
                                    #print('Error', bimestral)
                                    pass
                                else:
                                    if bimestral == '0':
                                        bimestrais.append(0)
                                    else:
                                        try:
                                            position = teachersNames.index(f'{bimestral[0]}')
                                        except:
                                            print('PROFESSOR NÃO ENCONTRADO : ', bimestral[0], turma)
                                            pass
                                        passou = False
                                        for h_professor in teachers[position].h_individuais:
                                            # Se os horários forem iguais
                                            if h_professor.turm[0] == turma:
                                                if bimestral[1] in h_professor.subject:
                                                    
                                                    # Colocamos o horário naquela posição
                                                    bimestrais.append(h_professor)
                                                    # Removemos ele da lista de horários que o professor tem que colocar
                                                    teachers[position].h_individuais.remove(h_professor)
                                                    passou = True
                                                    break
                                        if not passou:
                                            dia.append(0)
                                            print(f'Horário não encontrado: ({h_professor.turm}, {turma}), ({h_professor.subject},{bimestral[1]})')
                                            discordancia = True
                            dia.append(bimestrais)
                                    


                        try:
                            h = h.split('-')
                            if len(h) != 2:
                                #print('Error', h)
                                pass
                            else:
                                 # Correlacionamos o nome do professor com o Objeto professor já criado, e colocamos aquele horário aqui.
                                position = teachersNames.index(f'{h[0]}')
                                passou = False
                                for h_professor in teachers[position].h_individuais:
                                    # Se os horários forem iguais
                                    if h_professor.turm[0] == turma and h[1] in h_professor.subject:
                                        # Colocamos o horário naquela posição
                                        dia.append(h_professor)
                                        # Removemos ele da lista de horários que o professor tem que colocar
                                        teachers[position].h_individuais.remove(h_professor)
                                        passou = True
                                        break
                            if not passou:
                                dia.append(0)
                                print(f'Horário não encontrado: ({h_professor.turm}, {turma}), ({h_professor.subject},{h[1]})')
                                discordancia = True
                        except: pass
                        # Correlacionamos o nome do professor com o Objeto professor já criado, e colocamos aquele horário aqui.
                        
            if discordancia:
                #print('DISCORDÂNCIA')
                #print(df[df.columns[c]])
                #print(dia)
                break
            dia = [dia[0:6], dia[6:12], dia[12:]]
            #print(dia)
                
    

#lista_com_objt_professores, lista_com_nomes_professores = organizando_dados_da_planilha()
#get_functional_grade('Planilha funcional', teachers=lista_com_objt_professores, teachersNames=lista_com_nomes_professores)



from functions import loadData

data = loadData.getDatabase('Planilha dos horários.xlsx') 
lista = list(data.keys())

# Lista de colunas 
valores = list(data.values())
soma = 0

# Preciso juntar ano e subgrupo
salas = {}
turmas = ['MCT',  'ELT', 'MEC']
for c in range(0, len(valores[0])):
    valores[5][c] = 'NA' if valores[5][c] == 0 else valores[5][c]
    for turm in range(12, len(turmas) + 12):
        
        if valores[turm][c]:
            # Se o tipo do horário for bimestral, e ele for do tipo T, devemos dividir o horário por 2
            if valores[6][c] == 2 or valores[6][c] == 4:
                n_horarios = valores[turm][c]/2

            # Se o horário for bimestral e do tipo G, precisamos dividir o resultado por 3
            elif valores[7][c] == 'G' or valores[6][c] == 1:
                n_horarios = valores[turm][c]/4

            try:
                salas[f'{turmas[turm - 12]}-{valores[3][c]}{valores[8][c]}'] += n_horarios
            except:
                salas[f'{turmas[turm - 12]}-{valores[3][c]}{valores[8][c]}'] = n_horarios
for k, i in salas.items():
    if ('N' in k) and (i > 20):
        print(k, '||', i , '(20)')
    if not('N' in k) and (i > 30):
        print(k, '||', i, '(30)')

    
    
    
        



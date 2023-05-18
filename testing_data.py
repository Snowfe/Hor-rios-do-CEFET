from functions import loadData

data = loadData.getDatabase('Planilha dos horários.xlsx') 
lista = list(data.keys())
valores = list(data.values())
soma = 0

# Preciso juntar ano e subgrupo
salas = {}
turmas = ['MCT',  'ELT', 'MEC']
for c in range(0, len(valores[0])):
    valores[5][c] = 'NA' if valores[5][c] == 0 else valores[5][c]
    for turm in range(9, len(turmas) + 9):
        if valores[turm][c]:
            n_horarios = valores[turm][c]/4 if valores[4][c] else valores[turm][c]
            try:
                salas[f'{turmas[turm - 9]}-{valores[3][c]}{valores[5][c]}'] += n_horarios
            except:
                salas[f'{turmas[turm - 9]}-{valores[3][c]}{valores[5][c]}'] = n_horarios
for k, i in salas.items():
    if ('N' in k) and (i > 20):
        print(k, '||', i , '(20)')
    if not('N' in k) and (i > 30):
        print(k, '||', i, '(30)')
    
    
    
        



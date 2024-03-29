import random
import re


class Teacher:
    def __init__(self, name, subject, type, prefers, limits, bimestral, local, horaries=""):
        self.name = name

        # Formato = cada matéria será adicionada nesta lista, com a seguinte formatação nome:turma,ex.:Matematica-2A
        self.subjects = [subject]

        # Formato = semelhante ao de cima, tendo as opções: manha, tarde ou noite
        self.types = [type]

        # Formato = haverá uma lista para cada uma das matérias, tendo o seguinte formato S ou N dia:horário inicial
        # - horário final, ex.: "S6:2,4", ou seja, prefere dar aula na sexta entre os horários 2 e 4
        self.prefers = [prefers]

        # Formato = segue o mesmo do acima, tendo a formatação N dia:horário inicial - horário final, ex.: N5:3,5,
        # ou seja, não pode quinta nos horários 3 a 5
        self.limits = [limits]

        # Horários durante a semana do professor
        self.schedule = {
            '2': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],  # manhã, tarde e noite
            '3': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
            '4': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
            '5': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
            '6': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0]]
        }

        # Formato = {subject: {Turm: classesInTheTurm}}, ex.: {'Matematica-1A': {MCT-1A: 4, ...}}
        self.horaries = {}
        self.horaries[subject] = horaries

        # Quantidade de objetos "Horários" que o professor tem -> total de aulas que ele dá na semana
        self.classes = 0

        # Se o horário for de uma matéria bimestral na posição tal da lista estará 1, senão estará 0
        self.bimestral = [int(bimestral[0])]

        # Todos os objetos "Horários" relacionados a esse professor
        self.h_individuais = []

        # Definimos se a metéria será no c1 ou no c2.
        self.locais = [local]

    def __repr__(self):
        return f'{self.name}'


class Turm:
    def __init__(self, name, year, group):
        self.name = f'{name}-{year}{group}'  # ex.: MEC-3B
        self.schedule = {'2': [], '3': [], '4': [], '5': [], '6': []}  # Horários durante a semana da turma


class Room:
    def __init__(self, name, position, limits, preDefinedSchedule=''):
        self.name = name
        self.position = position
        self.limits = limits
        self.schedule = {
            '2': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]],  # manhã e tarde
            '3': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]],
            '4': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]],
            '5': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]],
            '6': [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
        }


class Horario:
    def __init__(self, teacher, subject, turm, tipo, possible_h=0, local='c1', coteacher=0):
        self.teacher = teacher
        self.subject = subject
        self.turm = turm
        self.possible_h = possible_h
        self.local = local
        self.type = tipo 
        self.coteacher = coteacher

        # self.position = None

    def __repr__(self):
        return f"{self.teacher}-{self.subject.split('-')[0]}"


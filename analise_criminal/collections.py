from collections import namedtuple

class Response:
	def __init__(self, field, num, type):
		self.field = field
		self.num   = num
		self.type  = type

MONTHNAMES = {
	1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 
	6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 
	11: 'Novembro', 12: 'Dezembro'
}

## python's weekdays, as int, translated to string
WEEKDAYS = {
	0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira', 3: 'Quinta-feira',
	4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo'
}

## django's weekdays, as int, translated to string
WEEKDAYS_DJANGO = {
	1: 'Domingo', 2: 'Segunda-feira', 3: 'Terça-feira', 4: 'Quarta-feira', 
	5: 'Quinta-feira', 6: 'Sexta-feira', 7: 'Sábado'
}
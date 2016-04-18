def update(x, **entries):
	if isinstance(x, dict):
		x.update(entries)
	else:
		x.__dict__.update(entries)
	return x

class Struct:
	def __init__(self, **entries):
		self.__dict__.update(entries)

	def __repr__(self):
		args = ['%s=%r' % (k, v) for k, v in vars(self).items()]
		return 'Struct(%s)' % ', '.join(args)


class Response:
	def __init__(self, field, num, type):
		self.field = field
		self.num   = num
		self.type  = type


class BarGraph:
	def __init__(self, x, y, plot_type, title, color):
		self.x = x
		self.y = y
		self.type = plot_type
		self.title = title
		self.color = color

class Graph:
	def __init__(self, plot, title, color):
		self.type = plot
		self.title = title
		self.color = color

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
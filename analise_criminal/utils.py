from functools import reduce

### vars
MONTHNAMES = {
	1: 'Janeiro',  2: 'Fevereiro', 3: 'Março',     4: 'Abril',
	5: 'Maio',	   6: 'Junho', 	   7: 'Julho', 	   8: 'Agosto',
	9: 'Setembro', 10: 'Outubro',  11: 'Novembro', 12: 'Dezembro'
}

## python's weekdays, as int, translated to string
WEEKDAYS = {
	0: 'Segunda-feira', 1: 'Terça-feira',
	2: 'Quarta-feira',  3: 'Quinta-feira',
	4: 'Sexta-feira',   5: 'Sábado', 6: 'Domingo'
}

## django's weekdays, as int, translated to string
WEEKDAYS_DJANGO = {
	1: 'Domingo', 	   2: 'Segunda-feira',
	3: 'Terça-feira',  4: 'Quarta-feira',
	5: 'Quinta-feira', 6: 'Sexta-feira', 7: 'Sábado'
}


### functions

def str_to_int(s):
    try:
        return int(s)
    except ValueError:
        pass

def lmap(fn, *iterable):
	return list(map(fn, *iterable))

def lfilter(fn, iterable):
	return list(filter(fn, iterable))

def conj(coll, *vals):
	"conj(oin); like Clojure's"
	if isinstance(coll, list) or isinstance(coll, tuple):
		conj_vals(coll, *vals)
	else: # for objects and dicts
		conj_keyvals(coll, *vals)
	return coll

def conj_vals(coll, *vals):
	if isinstance(coll, list):
		def accumulate(acc, v):
			acc.append(v)
			return acc
		reduce(accumulate, vals, coll)
	elif isinstance(coll, tuple):
		coll += vals
	return coll

def conj_keyvals(dct, *keyvals):
	if isinstance(dct, dict):
		def accumulate(acc, kv):
			acc.update(kv)
			return acc
		reduce(accumulate, keyvals, dct)
	else:
		def accumulate(acc, kv):
			acc.__dict__.update(kv)
			return acc
		reduce(accumulate, keyvals, dct)
	return dct

### Classes

class Struct:
	"A generic container for simple data structures."

	def __init__(self, **entries):
		self.__dict__.update(entries)

	def __repr__(self):
		args = ['%s=%r' % (k, v) for k, v in vars(self).items()]
		return '<Struct(%s)>' % ', '.join(args)

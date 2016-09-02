from .utils import MONTHNAMES, lmap
from .commons import NATUREZAS, count_objs

def get_axis(
    objs, fn_x=lambda x: x.get('field'), fn_y=lambda y: y.get('num')):
    """
    Processes 'objs' inside a genexp as to get the x and y axis.
    - Takes a list of objects and two functions that will be used to
    define how the obj will be returned.
    - The functions default to return x.field and y.num.
    - Returns a tuple of lists of 'xaxis' and 'yaxis'.
    """
    xaxis = lmap(fn_x, objs)
    yaxis = lmap(fn_y, objs)
    return xaxis, yaxis

def naturezas_pie(qs):
    labels = lmap(lambda n: n.nome, NATUREZAS)
    values = lmap(lambda n: qs.filter(naturezas=n).count(),
                  NATUREZAS)
    return labels, values

def append_axis(data_lst, names):
    """
    `data_list` is a dict of keys `tag`, `a` data and `b` data
    `names` is a dict of keys `a` tag and `b` tag
    """
    context_dct = OrderedDict()
    for data in data_lst:
        tag = data['tag']
        xaxis1, yaxis1 = get_axis(data['a'])
        xaxis2, yaxis2 = get_axis(data['b'])
        context_dct[tag] = [
            {'x': xaxis1, 'y': yaxis1, 'id': 'id_%s_graph' % tag,
            'color': 'rgb(255,0,0)', 'name': names['a']},
            {'x': xaxis2, 'y': yaxis2, 'id': 'id_%s_graph' % tag,
            'color': 'rgb(255,255,0)', 'name': names['b']},
        ]
    return context_dct

def count_months(queryset):
    """
    Takes a queryset; counts records by months and returns
    them inside a dict.
    """
    return count_objs(
        queryset, delimitor=range(1, 13), type="Mês",
        qs_filtering_fn=lambda qs, i: qs.filter(data__month=i),
        field_name_fn=lambda qs: MONTHNAMES[qs[0].data.month])

def make_graph(func, queryset, fields, plot, title, color=''):
	"""
	Takes several args required to make a Plotly graph, plus a function,
	which will do the work of generating the fields required.
	Returns a Graph object.
	"""
	field, occurrences = func(
		queryset.values(fields[0]).annotate(num=Count('id')), fields[0])
	return Struct(x=field, y=occurrences, plot_type=plot,
				  title=title, color=color)

def make_days_graph(queryset, plot, title, color=''):
	"""
	Returnes a Graph object with the necessary properties
	to make a Plotly graph with days.
	"""
	return make_graph(func=fetch_graph_data, queryset=queryset,
		fields=['data'], plot=plot, title=title, color=color)

def make_neighborhood_graph(queryset, plot, title, color=''):
	"""
	Returnes a Graph object with the necessary properties
	to make a Plotly graph with days.
	"""
	return make_graph(func=fetch_graph_data, queryset=queryset,
		fields=['bairro'], plot=plot, title=title, color=color)

def make_street_graph(queryset, plot, title, color=''):
	"""
	Returnes a Graph object with the necessary properties
	to make a Plotly graph with days.
	"""
	return make_graph(func=fetch_graph_data, queryset=queryset,
		fields=['via'], plot=plot, title=title, color=color)

def make_nature_graph(queryset, plot, title, color=''):
	"""
	Returnes a Graph object with the necessary properties
	to make a Plotly graph with days.
	"""
	return make_graph(func=fetch_graph_data, queryset=queryset,
		fields=['natureza'], plot=plot, title=title, color=color)

def make_hours_graph(queryset, plot, title, color=''):
	"""
	Returnes a Graph object with the necessary properties
	to make a Plotly graph with hours.
	"""
	return make_graph(func=fetch_graph_hour, queryset=queryset,
		fields=['hora'], plot=plot, title=title, color=color)

def fetch_graph_data(objs, fields):
	"Returns two lists"
	field = [str(obj.get(fields)) for obj in objs]
	occurrences = [obj.get('num') for obj in objs]
	return field, occurrences

def fetch_graph_hour(objs, fields):
	"Fetchs occurrences per hour."
	# It's slightly more complicated than the others, because the hour fields
	# are duplicated, since they can have happened in different minutes inside
	# the hours. Hence, we have to loop through the qs, accumulating the occur-
	# rences per hour before we can loop again, generating the final list of
	# fields and occurrences.
	container = OrderedDict()
	for obj in objs:
		if not obj.get(fields):
			continue
		key = obj.get(fields).hour
		val = obj.get('num')
		if container.get(key):
			container[key] += val
		else:
			container[key] = val
	field = [hora for hora in container.keys()]
	occurrences = [val for val in container.values()]
	return field, occurrences

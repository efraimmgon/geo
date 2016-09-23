from collections import OrderedDict
from functools import reduce
from django.db.models import Count

from .utils import MONTHNAMES, lmap, lfilter, conj
from .commons import NATUREZAS, NATUREZAS_ID_ALL, get_weekdays

def get_axis(objs,
             fn_x=lambda x: x.get('field'),
             fn_y=lambda y: y.get('num')):
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
    Accumulates the data of two periods, formatting the result
    for usage as a plotting, with x and y axis, an id for
    the html elt, a display name and color.
    - `data_list` is a dict of keys `tag`, `a` data and `b` data
    - `names` is a dict of keys `a` tag and `b` tag
    """
    def acc_helper(acc, row):
        tag = row['tag']
        xaxis1, yaxis1 = get_axis(row['a'])
        xaxis2, yaxis2 = get_axis(row['b'])
        r = lmap(lambda x, y, name, rgb: \
                 {'x': x, 'y': y, 'id': 'id_%s_graph' % tag,
                  'color': rgb, 'name': name},
                 (xaxis1, xaxis2), (yaxis1, yaxis2), (names['a'], names['b']),
                 ('rgb(255, 0, 0)', 'rgb(255,255,0)'))
        return conj(acc, {tag: r})

    return reduce(acc_helper, data_lst, OrderedDict())

## Note: to generate a plot from more than one field
## one has to simply make `field` accept a tuple and
## adapt the code accordingly
def make_graph(fn, qs, field, plot, title, color=''):
    """
    Takes several args required to make a Plotly graph, plus a function,
    which will do the work of generating the field required.
    Returns a Graph object.
    """
    qs_list = qs.select_related("cidade").values(field).annotate(num=Count('id'))
    qs_list = qs_list.order_by('num')
    field, occurrences = fn(qs_list, field)
    return {'x': field, 'y': occurrences, 'type': plot,
            'title': title, 'color': color}

def make_days_graph(qs, plot, title, color=''):
    """
    Returnes a Graph object with the necessary properties
    to make a Plotly graph with days.
    """
    return make_graph(fn=fetch_graph_data, qs=qs,
        field='data', plot=plot, title=title, color=color)

def make_neighborhood_graph(qs, plot, title, color=''):
    """
    Returnes a Graph object with the necessary properties
    to make a Plotly graph with days.
    """
    return make_graph(fn=fetch_graph_data, qs=qs,
        field='bairro', plot=plot, title=title, color=color)

def make_street_graph(qs, plot, title, color=''):
    """
    Returnes a Graph object with the necessary properties
    to make a Plotly graph with days.
    """
    return make_graph(fn=fetch_graph_data, qs=qs,
        field='via', plot=plot, title=title, color=color)

def make_nature_graph(qs, plot, title, color=''):
    """
    Returnes a Graph object with the necessary properties
    to make a Plotly graph with days.
    """
    return make_graph(fn=fetch_graph_data, qs=qs,
        field='naturezas', plot=plot, title=title, color=color)

def make_hours_graph(qs, plot, title, color=''):
    """
    Returnes a Graph object with the necessary properties
    to make a Plotly graph with hours.
    """
    return make_graph(fn=fetch_graph_hour, qs=qs,
        field='hora', plot=plot, title=title, color=color)

def make_month_graph(qs, plot, title, color=''):
    return make_graph(fn=count_months, qs=qs, field='hora', plot=plot,
                      title=title, color=color)

def make_weekday_graph(qs, plot, title, color=''):
    result = get_weekdays(qs)
    field = lmap(lambda r: r['field'], result)
    occurrences = lmap(lambda r: r['num'], result)
    return {'x': field, 'y': occurrences, 'type': plot,
            'title': title, 'color': color}

def count_months(qs, field=None):
    """
    Takes a queryset; counts records by months and returns
    them inside a dict.
    """
    result = reduce(lambda acc, i: \
                    conj(acc, {'field': MONTHNAMES[i],
                               'num': qs.filter(data__month=i).count()}),
                    range(1, 13), [])
    result = lfilter(lambda r: r['num'] != 0, result)
    field = lmap(lambda row: row['field'], result)
    occurrences = lmap(lambda row: row['num'], result)
    return field, occurrences

def fetch_graph_data(qs_list, field):
    "Returns two lists"
    if field == 'naturezas':
        # qs_list returns the pk of naturezas, so we need to map it to its name
        helper = lambda row: NATUREZAS_ID_ALL[row[field]]
    else:
        helper = lambda row: str(row[field])
    field = lmap(helper, qs_list)
    occurrences = lmap(lambda row: row['num'], qs_list)
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


plot_function = {
    "naturezas": make_nature_graph,
    "bairro": make_neighborhood_graph,
    "via": make_street_graph,
    "dia da semana": make_weekday_graph,
    "dia": make_days_graph,
    "mês": make_month_graph,
}

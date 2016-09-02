from django.db.models import Count

from datetime import time
from unicodedata import normalize
from collections import OrderedDict
from functools import reduce

from setup_app.models import Ocorrencia, Natureza
from .utils import (
    MONTHNAMES, WEEKDAYS, WEEKDAYS_DJANGO, Struct, lmap, conj
)

## furto, roubo, uso, homicídio, tráfico; excluding associação
nats = [
 (3, 'Furto'),
 (4, 'Homicídio Culposo'),
 (5, 'Homicídio Doloso'),
 (6, 'Roubo'),
 (7, 'Tráfico Ilícito de Drogas'),
 (8, 'Uso Ilícito de Drogas')
]

NATUREZAS = lmap(lambda n: Natureza.objects.get(pk=n[0]), nats)
NATUREZAS_ID = reduce(lambda acc, n: conj(acc, {n.pk: n.nome}),
                      NATUREZAS, {})
NATUREZAS_ID_ALL = reduce(lambda acc, n: conj(acc, {n.pk: n.nome}),
                       Natureza.objects.all(), {})
PERIODOS = ('00:00 - 05:59', '06:00 - 11:59', '12:00 - 17:59', '18:00 - 23:59')


def process_report_arguments(form_report, form_filter):
    """
    Uses user's selections to decide what analysis to process,
    and what data to present.
    """
    TAGS = {
        'natures': '5 naturezas com maior registro',
        'records': '5 ocorrências com maior registro',
        'neighborhoods': '5 bairros com maior registro',
        'roads': '5 vias com maior registro',
        'places': '5 locais com maior registro',
        'weekdays': 'Registros por dia da semana',
        'time': 'Registros por horário'
    }

    context = {}
    A = Struct()
    B = Struct()

    ## context is composed of the following keys:
    # forms; dates; total; axis; basico; comparison; filtro; bairro; detalhaento
    context['forms'] = {'report': form_report, 'filter': form_filter}

    A.start = form_report.cleaned_data['data_inicial_a']
    A.end   = form_report.cleaned_data['data_final_a']
    B.start = form_report.cleaned_data['data_inicial_b']
    B.end   = form_report.cleaned_data['data_final_b']

    city = form_filter.cleaned_data['cidade']

    o1 = Ocorrencia.objects.select_related('cidade').filter(
        data__gte=A.start, data__lte=A.end, cidade=city)
    o2 = Ocorrencia.objects.select_related('cidade').filter(
        data__gte=B.start, data__lte=B.end, cidade=city)

    total_a, total_b = o1.count(), o2.count()

    context['a'] = {
        'start': A.start,
        'end': A.end,
        'total': total_a
    }
    context['b'] = {
        'start': B.start,
        'end': B.end,
        'total': total_b
    }

    # GENERAL ANALYSIS + GRAPHS
    if form_report.cleaned_data['opts'] == 'Sim':
        a, comparison1, horarios1 = process_args(o1, compare=True)
        naturezas1, bairros1, vias1, locais1, weekdays1 = a

        b, comparison2, horarios2 = process_args(o2, compare=True)
        naturezas2, bairros2, vias2, locais2, weekdays2 = b

        # GRAPHS
        context['axis'] = OrderedDict()
        context['axis'].update(
            append_axis(
                data_lst=[{'tag': 'naturezas', 'a': naturezas1, 'b': naturezas2},
                          {'tag': 'bairros', 'a': bairros1, 'b': bairros2},
                          {'tag': 'vias', 'a': vias1, 'b': vias2},
                          {'tag': 'horários', 'a': horarios1, 'b': horarios2}],
                names={'a': 'Período A', 'b': 'Período B'}
            )
        )

        wd_xaxis1, wd_yaxis1 = get_axis(weekdays1)
        wd_xaxis2, wd_yaxis2 = get_axis(weekdays2)
        context['axis']['Dias da semana'] = [
            {'x': wd_xaxis1, 'y': wd_yaxis1, 'id': 'id_weekday_graph_a',
            'color': 'rgb(255,0,0)', 'name': 'Período A'},
            {'x': wd_xaxis2, 'y': wd_yaxis2, 'id': 'id_weekday_graph_a',
            'color': 'rgb(255,255,0)', 'name': 'Período B'},
        ]

        def map_helper(qs, id):
            labels = lmap(lambda n: n.nome, NATUREZAS)
            values = lmap(lambda n: qs.filter(naturezas=n).count(),
                          NATUREZAS)
            return {'labels': labels, 'values': values, 'id': id}

        context['axis']['pie'] = lmap(map_helper,
                                    [o1, o2], ['pie_a', 'pie_b'])

        # Percentage fluctuation from A to B
        context['comparison'] = lmap(lambda a, b: \
            {'a': a, 'b': b, 'variation': get_percentage(a['num'], b['num'])},
            comparison1, comparison2)

        context['variation'] = get_percentage(total_a, total_b)

        context['basico'] = [
            {TAGS['records']: [naturezas1, naturezas2]},
            {TAGS['neighborhoods']: [bairros1, bairros2]},
            {TAGS['roads']: [vias1, vias2]},
            {TAGS['places']: [locais1, locais2]},
            {TAGS['weekdays']: [weekdays1, weekdays2]},
            {TAGS['time']: [horarios1, horarios2]},
        ]
    # End of General Analysis + Graphs

    # Analysis of specific Naturezas
    ## TODO: refactor code to stop repetition of code
    if form_filter.cleaned_data['naturezas']:

        detail_keys = [TAGS['neighborhoods'], TAGS['roads'], TAGS['places'],
                       TAGS['weekdays'], TAGS['time']]

        def loop_over_natureza(n, querysets, acc=tuple()):
            if querysets:
                qs = querysets[0]
                result = process_args(qs.filter(naturezas__nome__icontains=n))
                (naturezas, bairros, vias, locais, wd), _, horarios = result
                vals = bairros, vias, locais, wd, horarios
                return loop_over_natureza(n, querysets[1:],
                                          acc=conj(acc, vals))
            return acc

        def acc_naturezas(acc, n):
            ## get the data for each natureza
            vals1, vals2 = loop_over_natureza(n, (o1, o2))
            def keys_to_values(acc, keyvals):
                key, vals = keyvals
                return conj(acc, {key: vals})
            ## accumulate the keys populating it with data
            result = reduce(keys_to_values,
                            zip(detail_keys, zip(vals1, vals2)), OrderedDict())
            ## pair the result to its natureza
            return conj(acc, {n: result})

        r = reduce(acc_naturezas,
                   map(lambda n: normalize('NFKD', n),
                       form_filter.cleaned_data['naturezas']),
                   OrderedDict())
        context['filtro'] = r

    # Analysis of a specific neighborhood
    if form_filter.cleaned_data['bairro']:
        bairro = normalize('NFKD', form_filter.cleaned_data['bairro'])
        (naturezas1, _, vias1, _, weekdays1), _, horarios1 = process_args(
            o1.filter(bairro__icontains=bairro), compare=False)
        (naturezas2, _, vias2, _, weekdays2), _, horarios2 = process_args(
            o2.filter(bairro__icontains=bairro), compare=False)

        context['bairro_detail'] = bairro
        context['detail'] = [
            {TAGS['records']: [naturezas1, naturezas2]},
            {TAGS['roads']: [vias1, vias2]},
            {TAGS['weekdays']: [weekdays1, weekdays2]},
            {TAGS['time']: [horarios1, horarios2]},
        ]
    if form_filter.cleaned_data['details']:
        context['detalhamento'] = OrderedDict()

        if 'weekdays' in form_filter.cleaned_data['details']:
            detail_keys = [TAGS['natures'], TAGS['neighborhoods'], TAGS['roads'],
                           TAGS['places'], TAGS['time']]

            def loop_over_weekdays(index, querysets, acc=tuple()):
                if querysets:
                    p = querysets[0]
                    (naturezas, bairros, vias, locais, wd), _, horarios = process_args(p.filter(data__week_day=index))
                    vals = naturezas, bairros, vias, locais, horarios
                    return loop_over_weekdays(index, querysets[1:], acc=conj(acc, vals))
                return acc

            ## acc keyvals
            def acc_weekdays(acc, i):
                ## get the data for each day of the week
                vals1, vals2 = loop_over_weekdays(i, (o1,o2))
                def keys_to_values(acc, keyvals):
                    key, vals = keyvals
                    return conj(acc, {key: vals})
                ## accumulate the keys of the weekday populating it with data
                result = reduce(keys_to_values,
                                zip(detail_keys, zip(vals1, vals2)), OrderedDict())
                ## map the int to a str with the respective name
                return conj(acc, {WEEKDAYS_DJANGO[i]: result})

            r = reduce(acc_weekdays, range(1, 8), OrderedDict())
            context['detalhamento']['semana'] = r

        if 'time' in form_filter.cleaned_data['details']:
            detail_keys = [TAGS['natures'], TAGS['neighborhoods'], TAGS['roads'],
                           TAGS['places'], TAGS['weekdays']]

            def loop_over_periods(index, querysets, acc=tuple()):
                if querysets:
                    p = querysets[0]
                    (naturezas, bairros, vias, locais, wd), _, horarios = process_args(p.filter(periodo=PERIODOS[index]))
                    vals = naturezas, bairros, vias, locais, wd
                    return loop_over_periods(index, querysets[1:], acc=conj(acc, vals))
                return acc

            ## acc keyvals
            def acc_periods(acc, i):
                ## get the data for each period
                vals1, vals2 = loop_over_periods(i, (o1,o2))
                def keys_to_values(acc, keyvals):
                    key, vals = keyvals
                    return conj(acc, {key: vals})
                ## accumulate the keys of the periods populating it with data
                result = reduce(keys_to_values,
                                zip(detail_keys, zip(vals1, vals2)), OrderedDict())
                ## map the int to a str with the respective name
                return conj(acc, {PERIODOS[i]: result})


            r = reduce(acc_periods, range(len(PERIODOS)), OrderedDict())
            context['detalhamento']['horários'] = r

    return context


def process_args(qs, compare=False):
    """
    Takes a qs and an optional compare arg; returns generated data.
    Generates data with the given qs; if compare is true, also
    generates comparison data.
    """
    qs_for_naturezas = qs.select_related('cidade', 'naturezas')
    naturezas = get_qslist(qs_for_naturezas, 'naturezas')

    qs_for_bairros = qs.exclude(bairro=None).select_related('cidade')
    bairros = get_qslist(qs_for_bairros, 'bairro')

    qs_for_vias = qs.exclude(via=None).select_related('cidade')
    vias = get_qslist(qs_for_vias, 'via')

    qs_for_local = qs.exclude(bairro=None).exclude(via=None)
    locais = get_qslist(qs_for_local.select_related('cidade'), 'bairro', 'via')

    weekdays = get_weekdays(qs)

    qs_for_periodo = qs.exclude(periodo=None).select_related('cidade')
    periods = get_qslist(qs_for_periodo, 'periodo')

    # data fluctuation of a in relation to b, and vice-versa
    comparison = []
    if compare:
        comparison = lmap(lambda n: get_comparison_data(qs, n),
                         NATUREZAS)
    return [(naturezas, bairros, vias, locais, weekdays), comparison, periods]

## unused
def get_weekdays(queryset):
    """
    Takes a queryset.
    Returns a dict, with 'field', 'num', and 'type' keys.
    """
    return count_objs(
        queryset, delimitor=range(1, 8), type="Dia da semana",
        qs_filtering_fn=lambda qs, i: qs.filter(data__week_day=i),
        ## fill in the respective descriptive weekday name
        field_name_fn=lambda qs: WEEKDAYS[qs[0].data.weekday()])

### Other functions

def calculate_variation(a, b):
    """
    Calculates variation relative from b to a.
    a < b: percent. of Increase, if a > b: percent. of decrease
    """
    if (b == 0):
        return 0
    return (abs(a - b) / b) * 100

def get_percentage(a, b):
    """
    Gets percentage using calculate_variation(), taking into
    account which args should go where.
    """
    a, b = int(a), int(b)
    if a < b:
        return calculate_variation(a, b)
    return calculate_variation(b, a)

def get_qslist(qs, *fields, limit=5):
    qs = qs.select_related("cidade").values(*fields).annotate(num=Count("id"))
    ## pass only as many as specified in `limit`
    qs = qs.order_by('-num')[:limit]
    ## pass only the pre-selected naturezas
    #if 'naturezas' in fields:
    #    qs = filter(lambda row: row["naturezas"] in NATUREZAS_ID.keys(), qs)

    def helper(field, row):
        ## returns the pk of naturezas, so we need to map it to its name
        if field == 'naturezas':
            return NATUREZAS_ID_ALL.get(row.get(field))
        return row.get(field)

    return lmap(lambda row: {
        #"field": " | ".join(fields),
        "field": ", ".join(lmap(lambda f: helper(f, row), fields)),
        "num": row.get("num"),
        "type": " & ".join(fields)
        },
        ## returns a list of dicts with the keys `id` and the ones on `fields`
        qs)

def get_comparison_data(queryset, param):
    try:
        data = queryset.filter(naturezas=param).values(
            'naturezas').annotate(num=Count('id'))
        acc = lmap(lambda row: row['num'], data)
        return {'natureza': param, 'num': sum(acc)}
    except IndexError:
        return {'natureza': param, 'num': 0}


### Count occurrences of specific objects

def count_objs(queryset, delimitor, type, qs_filtering_fn, field_name_fn):
    """
    Used for getting the records per month and week.
    Returns a dict, containing a field, num, and type keys.

    INPUTS
    queryset: a queryset
    delimitor: a delimiting range, serving as the iteration's index;
    type: a type label for the dict response;
    qs_filtering_fn: a function that takes the queryset and index as input;
    field_name_fn: a function that takes the queryset, prior to saving it in
    field;
    """
    acc = []
    for i in delimitor:
        qs = qs_filtering_fn(queryset, i)
        try:
            acc.append(dict(field=field_name_fn(qs), num=qs.count(), type=type))
        except IndexError:
            continue
    return acc

def count_months(queryset):
    """
    Takes a queryset; counts records by months and returns
    them inside a dict.
    """
    return count_objs(
        queryset, delimitor=range(1, 13), type="Mês",
        qs_filtering_fn=lambda qs, i: qs.filter(data__month=i),
        field_name_fn=lambda qs: MONTHNAMES[qs[0].data.month])


### Ploting functions

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

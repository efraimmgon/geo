from django.db.models import Count

from datetime import time
from unicodedata import normalize
from collections import OrderedDict
from functools import reduce

from setup_app.models import Ocorrencia, Natureza
from .utils import (WEEKDAYS, WEEKDAYS_DJANGO, Struct, lmap, lfilter, conj,
                    str_to_int)
from .plotting import get_axis, append_axis
from .commons import count_objs, count_weekdays

# Global vars ----------------------------------------------------------

from .commons import NATUREZAS, NATUREZAS_ID_ALL
NATUREZAS_ID = reduce(lambda acc, n: conj(acc, {n.pk: n.nome}),
                      NATUREZAS, {})
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

    o1 = Ocorrencia.objects.filter(
        data__gte=A.start, data__lte=A.end, cidade=city)
    o2 = Ocorrencia.objects.filter(
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

    # GENERAL ANALYSIS + GRAPHS ---------------------------------------

    if form_report.cleaned_data['opts'] == 'Sim':
        a, comparison1, horarios1 = process_args(o1, compare=True)
        naturezas1, bairros1, vias1, locais1, weekdays1 = a

        b, comparison2, horarios2 = process_args(o2, compare=True)
        naturezas2, bairros2, vias2, locais2, weekdays2 = b

        ## GRAPHS ------------------------------------------------------

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

        ## naturezas pie ------------------------------------------------

        def helper(qs, id):
            dct = count_objs(qs.filter(naturezas__in=NATUREZAS), "naturezas")
            return {"labels": lmap(lambda k: NATUREZAS_ID_ALL[k].nome, dct),
                    "values": [v for k, v in dct.items()],
                    "id": id}

        context['axis']['pie'] = lmap(helper, [o1, o2], ['pie_a', 'pie_b'])

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
        ## the input gets here represented as a string of a list of ints
        form_naturezas_input = lmap(
             lambda item: \
                ## the input has chars that cannot be mapped to int, hence:
                lfilter(lambda x: x is not None,
                        map(str_to_int, list(item))),
             form_filter.cleaned_data['naturezas'])

        detail_keys = [TAGS['neighborhoods'], TAGS['roads'], TAGS['places'],
                       TAGS['weekdays'], TAGS['time']]

        def loop_over_natureza(n, querysets, acc=None):
            acc = acc if acc is not None else list()
            if querysets:
                qs = querysets[0]
                result = process_args(qs.filter(naturezas__in=n))
                (naturezas, bairros, vias, locais, wd), _, horarios = result
                vals = bairros, vias, locais, wd, horarios
                return loop_over_natureza(n, querysets[1:], conj(acc, vals))
            return acc

        def acc_naturezas(acc, n):
            ## get the data for each natureza
            ## TODO: the code queries the DB for natureza in -- is there
            ## a way to avoid this?
            vals1, vals2 = loop_over_natureza(n, (o1, o2))
            def keys_to_values(acc, keyvals):
                key, vals = keyvals
                return conj(acc, {key: vals})
            ## accumulate the keys populating it with data
            result = reduce(keys_to_values,
                            zip(detail_keys, zip(vals1, vals2)), OrderedDict())
            ## pair the result to its natureza and get the
            ## general name of the records
            key = NATUREZAS_ID_ALL[n[0]].nome.split(" ")[0]
            if "Assoc" in key:
                key = "Entorpecentes"
            return conj(acc, {key: result})

        context['filtro'] = reduce(acc_naturezas,
                                   form_naturezas_input, OrderedDict())

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

            def loop_over_weekdays(index, querysets, acc=None):
                acc = acc if acc is not None else list()
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

            # loop over qs mapping reports to their weekday
            r = reduce(acc_weekdays, range(1, 8), OrderedDict())
            context['detalhamento']['semana'] = r

        if 'time' in form_filter.cleaned_data['details']:
            detail_keys = [TAGS['natures'], TAGS['neighborhoods'], TAGS['roads'],
                           TAGS['places'], TAGS['weekdays']]

            def loop_over_periods(index, querysets, acc=None):
                acc = acc if acc is not None else list()
                if querysets:
                    (naturezas, bairros, vias, locais, wd), _, horarios = process_args(
                        querysets[0].filter(periodo=PERIODOS[index]))
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

    weekdays = [{'field': WEEKDAYS[k],
                 'num': v,
                 'type': "Dia da semana"}
                for k,v in count_weekdays(qs).items()]

    qs_for_periodo = qs.exclude(periodo=None).select_related('cidade')
    periods = get_qslist(qs_for_periodo, 'periodo')

    # data fluctuation of a in relation to b, and vice-versa
    comparison = []
    if compare:
        comparison = [{"natureza": NATUREZAS_ID_ALL[key],
                       "num": val}
                      for key, val in count_objs(qs, "naturezas", 5).items()]

    return [(naturezas, bairros, vias, locais, weekdays), comparison, periods]

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
    qs = qs.values(*fields).annotate(num=Count("id"))
    ## pass only as many as specified in `limit`
    qs = qs.order_by('-num')[:limit]
    ## pass only the pre-selected naturezas
    #if 'naturezas' in fields:
    #    qs = filter(lambda row: row["naturezas"] in NATUREZAS_ID.keys(), qs)

    def helper(field, row):
        ## returns the pk of naturezas, so we need to map it to its name
        if field == 'naturezas':
            return NATUREZAS_ID_ALL[row[field]].nome
        return row[field]

    return lmap(lambda row: {
            #"field": " | ".join(fields),
            "field": ", ".join(lmap(lambda f: helper(f, row), fields)),
            "num": row.get("num"),
            "type": " & ".join(fields)
            },
        ## returns a list of dicts with the keys `id` and the ones on `fields`
        qs)

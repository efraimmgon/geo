from django.db.models import Count
from functools import reduce
from collections import OrderedDict
from unicodedata import normalize

from setup_app.models import Natureza
from .utils import lmap, conj, WEEKDAYS_DJANGO, WEEKDAYS

## furto, roubo, uso, homicídio, tráfico; excluding associação
nats = [
 (3, 'Furto'),
 (4, 'Homicídio Culposo'),
 (5, 'Homicídio Doloso'),
 (6, 'Roubo'),
 (7, 'Tráfico Ilícito de Drogas'),
 (8, 'Uso Ilícito de Drogas')
]

### Global vars

NATUREZAS = Natureza.objects.filter(pk__in=lmap(lambda p: p[0], nats))

NATUREZAS_ID_ALL = reduce(lambda acc, n: conj(acc, {n.pk: n}),
                          Natureza.objects.all(), {})

ROUBO = [k for k,v in NATUREZAS_ID_ALL.items()
				if "roubo" in v.nome.lower()]
FURTO = [k for k,v in NATUREZAS_ID_ALL.items()
				if "furto" in v.nome.lower()]
TRAFICO = [k for k,v in NATUREZAS_ID_ALL.items()
				if normalize("NFKD", "tráfico") in v.nome.lower()]
HOMICIDIO = [k for k,v in NATUREZAS_ID_ALL.items()
				if normalize("NFKD", "homicídio") in v.nome.lower()]
DROGAS = [k for k,v in NATUREZAS_ID_ALL.items()
			if "drogas" in v.nome.lower()]


def count_weekdays(qs):
    """
    Takes a queryset and returns a dict with python's int representation
    of the weekdays as keys and the count of the weekdays in the qs.
    """
    qs_lst = qs.exclude(data=None).values("data").annotate(num=Count("data"))
    def accumulator(acc, obj):
        index = obj['data'].weekday()
        val = acc.get(index, 0)
        return conj(acc, {index: val+obj['num']})
    return reduce(accumulator, qs_lst, {})

def count_objs(qs, field, limit=None):
    qs_lst = qs.values(field).annotate(num=Count(field)).order_by('-num')
    if limit is not None:
        qs_lst = qs_lst[:limit]
    def accumulator(acc, obj):
        index = obj[field]
        val = acc.get(index, 0)
        return conj(acc, {index: val+obj['num']})
    return reduce(accumulator, qs_lst, OrderedDict())

def get_weekdays(qs):
    """
    Takes a queryset and returns a dict, with
    `field`, `num`, and `type` keys.
    """
    dct = count_weekdays(qs)
    def accumulator(acc, key):
        return conj(acc, {'field': WEEKDAYS[key],
                          'num': dct[key],
                          'type': "Dia da semana"})
    return reduce(accumulator, dct, [])

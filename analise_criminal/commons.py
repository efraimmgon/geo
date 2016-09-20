from django.db.models import Count
from functools import reduce

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

NATUREZAS = lmap(lambda n: Natureza.objects.get(pk=n[0]), nats)

NATUREZAS_ID_ALL = reduce(lambda acc, n: conj(acc, {n.pk: n.nome}),
                          Natureza.objects.all(), {})

def count_weekdays(qs):
    qs_lst = qs.exclude(data=None).values("data").annotate(num=Count("data"))
    def accumulator(acc, obj):
        index = obj['data'].weekday()
        val = acc.get(index, 0)
        return conj(acc, {index: val+obj['num']})
    return reduce(accumulator, qs_lst, {})

def get_weekdays(qs):
    dct = count_weekdays(qs)
    def accumulator(acc, key):
        return conj(acc, {'field': WEEKDAYS[key],
                          'num': dct[key],
                          'type': "Dia da semana"})
    return reduce(accumulator, dct, [])

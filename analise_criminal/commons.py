from functools import reduce
from setup_app.models import Natureza
from .utils import lmap, conj, WEEKDAYS_DJANGO

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

def get_weekdays(qs):
    """
    Takes a queryset.
    Returns a dict, with 'field', 'num', and 'type' keys.
    """
    return reduce(lambda acc, i: \
                  conj(acc, {'field': WEEKDAYS_DJANGO[i],
                             'num': qs.filter(data__week_day=i).count(),
                             'type': "Dia da semana"}),
                  range(1, 8), [])

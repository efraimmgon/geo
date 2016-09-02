from setup_app.models import Natureza
from .utils import lmap

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


### Functions

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

from django.test import TestCase
from analise_criminal.utils import (
    conj_vals, conj_keyvals, conj, lmap, lfilter)


class UtilsTest(TestCase):

    def test_conj_vals(self):
        ## With lists
        self.assertEqual(conj_vals([1, 2, 3], 4, 5, 6),
                         [1,2,3,4,5,6])
        ## With tuples
        self.assertEqual(conj_vals((1, 2, 3), 4, 5, 6),
                         (1,2,3,4,5,6))

    def test_conj_keyvals(self):
        ## With one dict
        self.assertEqual(conj_keyvals({"a": 1}, {"a": 0, "b": 1}),
                         {"a": 0, "b": 1})
        ## With two dicts
        self.assertEqual(conj_keyvals({}, {"a": 0}, {"b": 1}),
                         {"a": 0, "b": 1})

    def test_conj(self):
        ## list
        self.assertEqual(conj([1,2,3], 4, 5, 6),
                         [1, 2, 3, 4, 5, 6])
        ## tuple
        self.assertEqual(conj((1, 2, 3), 4, 5, 6),
                         (1, 2, 3))
        ## dict
        self.assertEqual(conj({"a": 1}, {"b": 2}, {"c": 3}),
                         {"a": 1, "b": 2, "c": 3})

    def test_lmap(self):
        self.assertEqual(lmap(lambda x: x*2, range(5)),
                         list(map(lambda x: x*2, range(5))))

    def test_lfilter(self):
        self.assertEqual(lfilter(lambda x: x%2 == 0, range(5)),
                         list(filter(lambda x: x%2 == 0, range(5))))

# -*- coding: utf-8 -*-
'''test stuf'''

from stuf.six import unittest


class Base(object):

    @property
    def _makeone(self):
        return self._impone(test1='test1', test2='test2', test3=dict(e=1))

    def setUp(self):
        self.stuf = self._makeone

    def test__getattr__(self):
        self.assertEqual(self.stuf.test1, 'test1')
        self.assertEqual(self.stuf.test2, 'test2')
        self.assertEqual(self.stuf.test3.e, 1)

    def test__getitem__(self):
        self.assertEqual(self.stuf['test1'], 'test1')
        self.assertEqual(self.stuf['test2'], 'test2')
        self.assertEqual(self.stuf['test3']['e'], 1)

    def test_get(self):
        self.assertEqual(self.stuf.get('test1'), 'test1')
        self.assertEqual(self.stuf.get('test2'), 'test2')
        self.assertIsNone(self.stuf.get('test4'), 'test4')
        self.assertEqual(self.stuf.get('test3').get('e'), 1)
        self.assertIsNone(self.stuf.get('test3').get('r'))

    def test__setattr__(self):
        self.stuf.max = 3
        self.stuf.test1 = 'test1again'
        self.stuf.test2 = 'test2again'
        self.stuf.test3.e = 5
        self.assertEqual(self.stuf.max, 3)
        self.assertEqual(self.stuf.test1, 'test1again')
        self.assertEqual(self.stuf.test2, 'test2again')
        self.assertEqual(self.stuf.test3.e, 5)

    def test__setitem__(self):
        self.stuf['max'] = 3
        self.stuf['test1'] = 'test1again'
        self.stuf['test2'] = 'test2again'
        self.stuf['test3']['e'] = 5
        self.assertEqual(self.stuf['max'], 3)
        self.assertEqual(self.stuf['test1'], 'test1again')
        self.assertEqual(self.stuf['test2'], 'test2again')
        self.assertEqual(self.stuf['test3']['e'], 5)

    def test__delattr__(self):
        del self.stuf.test1
        del self.stuf.test2
        del self.stuf.test3.e
        self.assertEqual(len(self.stuf.test3), 0)
        del self.stuf.test3
        self.assertEqual(len(self.stuf), 0)

    def test__delitem__(self):
        del self.stuf['test1']
        del self.stuf['test2']
        del self.stuf['test3']['e']
        self.assertNotIn('e', self.stuf['test3'])
        self.assertEqual(len(self.stuf['test3']), 0)
        del self.stuf['test3']
        self.assertEqual(len(self.stuf), 0)
        self.assertNotIn('test1', self.stuf)
        self.assertNotIn('test2', self.stuf)
        self.assertNotIn('test3', self.stuf)

    def test__cmp__(self):
        tstuff = self._makeone
        self.assertEqual(self.stuf, tstuff)

    def test__len__(self):
        self.assertEqual(len(self.stuf), 3)
        self.assertEqual(len(self.stuf.test3), 1)

    def test_repr(self):
        from stuf.six import strings
        self.assertIsInstance(repr(self._makeone), strings)
        self.assertIsInstance(repr(self.stuf), strings)

    def test_items(self):
        slist = list(self.stuf.items())
        self.assertIn(('test1', 'test1'), slist)
        self.assertIn(('test2', 'test2'), slist)
        self.assertIn(('test3', {'e': 1}), slist)

    def test_iteritems(self):
        slist = list(self.stuf.iteritems())
        self.assertIn(('test1', 'test1'), slist)
        self.assertIn(('test2', 'test2'), slist)
        self.assertIn(('test3', {'e': 1}), slist)

    def test_iter(self):
        slist = list(self.stuf)
        slist2 = list(self.stuf.test3)
        self.assertIn('test1', slist)
        self.assertIn('test2', slist)
        self.assertIn('test3', slist)
        self.assertIn('e', slist2)

    def test_iterkeys(self):
        slist = list(self.stuf.iterkeys())
        slist2 = list(self.stuf.test3.iterkeys())
        self.assertIn('test1', slist)
        self.assertIn('test2', slist)
        self.assertIn('test3', slist)
        self.assertIn('e', slist2)

    def test_itervalues(self):
        slist = list(self.stuf.itervalues())
        slist2 = list(self.stuf.test3.itervalues())
        self.assertIn('test1', slist)
        self.assertIn('test2', slist)
        self.assertIn({'e': 1}, slist)
        self.assertIn(1, slist2)

    def test_values(self):
        slist1 = self.stuf.test3.values()
        slist2 = self.stuf.values()
        self.assertIn(1, slist1)
        self.assertIn('test1', slist2)
        self.assertIn('test2', slist2)
        self.assertIn({'e': 1}, slist2)

    def test_keys(self):
        slist1 = self.stuf.test3.keys()
        slist2 = self.stuf.keys()
        self.assertIn('e', slist1)
        self.assertIn('test1', slist2)
        self.assertIn('test2', slist2)
        self.assertIn('test3', slist2)

    def test_pickle(self):
        import pickle
        tstuf = self._makeone
        pkle = pickle.dumps(tstuf)
        nstuf = pickle.loads(pkle)
        self.assertIsInstance(nstuf, self._impone)
        self.assertEqual(tstuf, nstuf)

    def test_clear(self):
        self.stuf.test3.clear()
        self.assertEqual(len(self.stuf.test3), 0)
        self.stuf.clear()
        self.assertEqual(len(self.stuf), 0)

    def test_pop(self):
        self.assertEqual(self.stuf.test3.pop('e'), 1)
        self.assertEqual(self.stuf.pop('test1'), 'test1')
        self.assertEqual(self.stuf.pop('test2'), 'test2')
        self.assertEqual(self.stuf.pop('test3'), {})

    def test_copy(self):
        tstuf = self._makeone
        nstuf = tstuf.copy()
        self.assertIsInstance(nstuf, self._impone)
        self.assertIsInstance(tstuf, self._impone)
        self.assertEqual(tstuf, nstuf)

    def test_popitem(self):
        item = self.stuf.popitem()
        self.assertEqual(len(item) + len(self.stuf), 4, item)

    def test_setdefault(self):
        self.assertEqual(self.stuf.test3.setdefault('e', 8), 1)
        self.assertEqual(self.stuf.test3.setdefault('r', 8), 8)
        self.assertEqual(self.stuf.setdefault('test1', 8), 'test1')
        self.assertEqual(self.stuf.setdefault('pow', 8), 8)

    def test_update(self):
        tstuff = self._makeone
        tstuff['test1'] = 3
        tstuff['test2'] = 6
        tstuff['test3'] = dict(f=2)
        self.stuf.update(tstuff)
        self.assertEqual(self.stuf['test1'], 3, self.stuf.items())
        self.assertEqual(self.stuf['test2'], 6)
        self.assertEqual(self.stuf['test3'], dict(f=2), self.stuf)

    def test_nofile(self):
        import sys
        s = self._impone(a=sys.stdout, b=1)
        self.assertEqual(s.a, sys.stdout)
        t = self._impone(a=[sys.stdout], b=1)
        self.assertEqual(t.a, [sys.stdout])


class TestStuf(Base, unittest.TestCase):

    @property
    def _impone(self):
        from stuf import stuf
        return stuf


class TestDefaultStuf(Base, unittest.TestCase):

    @property
    def _impone(self):
        from stuf import defaultstuf
        return defaultstuf

    @property
    def _makeone(self):
        return self._impone(
            list, test1='test1', test2='test2', test3=dict(e=1)
        )

    def test__getattr__(self):
        self.assertEqual(self.stuf.test1, 'test1')
        self.assertEqual(self.stuf.test2, 'test2')
        self.assertEqual(self.stuf.test4, [])
        self.assertEqual(self.stuf.test3.e, 1)
        self.assertEqual(self.stuf.test3.f, [])

    def test__getitem__(self):
        self.assertEqual(self.stuf['test1'], 'test1')
        self.assertEqual(self.stuf['test2'], 'test2')
        self.assertEqual(self.stuf['test4'], [])
        self.assertEqual(self.stuf['test3']['e'], 1)
        self.assertEqual(self.stuf['test3']['f'], [])

    def test__delattr__(self):
        del self.stuf.test1
        del self.stuf.test2
        del self.stuf.test3.e
        self.assertEqual(len(self.stuf.test3), 0)
        del self.stuf.test3
        self.assertEqual(len(self.stuf), 0)
        self.assertEqual(self.stuf.test1, [])
        self.assertEqual(self.stuf.test2, [])
        self.assertEqual(self.stuf.test3, [])
        self.assertRaises(AttributeError, lambda: self.stuf.test3.e)

    def test__delitem__(self):
        del self.stuf['test1']
        del self.stuf['test2']
        del self.stuf['test3']['e']
        self.assertNotIn('e', self.stuf['test3'])
        self.assertEqual(len(self.stuf['test3']), 0)
        self.assertEqual(self.stuf['test3']['e'], [])
        del self.stuf['test3']
        self.assertEqual(len(self.stuf), 0)
        self.assertNotIn('test1', self.stuf)
        self.assertNotIn('test2', self.stuf)
        self.assertNotIn('test3', self.stuf)
        self.assertEqual(self.stuf['test1'], [])
        self.assertEqual(self.stuf['test2'], [])
        self.assertEqual(self.stuf['test3'], [])
        self.assertRaises(TypeError, lambda: self.stuf['test3']['e'])

    def test_clear(self):
        self.stuf.test3.clear()
        self.assertEqual(len(self.stuf.test3), 0)
        self.assertEqual(self.stuf['test3']['e'], [])
        self.stuf.clear()
        self.assertEqual(len(self.stuf), 0)
        self.assertEqual(self.stuf['test1'], [])
        self.assertEqual(self.stuf['test2'], [])
        self.assertEqual(self.stuf['test3'], [])

    def test_nofile(self):
        import sys
        s = self._impone(list, a=sys.stdout, b=1)
        self.assertEqual(s.a, sys.stdout)
        t = self._impone(list, a=[sys.stdout], b=1)
        self.assertEqual(t.a, [sys.stdout])


class TestFixedStuf(Base, unittest.TestCase):

    @property
    def _impone(self):
        from stuf import fixedstuf
        return fixedstuf

    def test__setattr__(self):
        self.assertRaises(AttributeError, lambda: setattr(self.stuf, 'max', 3))
        self.stuf.test1 = 'test1again'
        self.stuf.test2 = 'test2again'
        self.stuf.test3.e = 5
        self.assertRaises(AttributeError, lambda: self.stuf.max)
        self.assertEqual(self.stuf.test1, 'test1again')
        self.assertEqual(self.stuf.test2, 'test2again')
        self.assertEqual(self.stuf.test3.e, 5)

    def test__setitem__(self):
        self.assertRaises(KeyError, lambda: self.stuf.__setitem__('max', 3))
        self.stuf['test1'] = 'test1again'
        self.stuf['test2'] = 'test2again'
        self.stuf['test3']['e'] = 5
        self.assertRaises(KeyError, lambda: self.stuf.__getitem__('max'))
        self.assertEqual(self.stuf['test1'], 'test1again')
        self.assertEqual(self.stuf['test2'], 'test2again')
        self.assertEqual(self.stuf['test3']['e'], 5)

    def test__delattr__(self):
        self.assertRaises(TypeError, lambda: delattr(self.stuf.test1))
        self.assertRaises(TypeError, lambda: delattr(self.stuf.test3.e))

    def test__delitem__(self):
        del self.stuf.test3['e']
        self.assertRaises(KeyError, lambda: self.stuf.test3['e'])
        del self.stuf['test1']
        self.assertRaises(KeyError, lambda: self.stuf['test1'])

    def test_clear(self):
        self.assertRaises(KeyError, lambda: self.stuf.__setitem__('max', 3))
        self.stuf.clear()
        self.stuf['test1'] = 'test1again'
        self.stuf['test3'] = 5

    def test_pop(self):
        self.assertRaises(AttributeError, lambda: self.stuf.test3.pop('e'))
        self.assertRaises(AttributeError, lambda: self.stuf.pop('test1'))

    def test_popitem(self):
        self.assertRaises(AttributeError, lambda: self.stuf.test3.popitem())
        self.assertRaises(AttributeError, lambda: self.stuf.popitem())

    def test_setdefault(self):
        self.assertEqual(self.stuf.test3.setdefault('e', 8), 1)
        self.assertRaises(KeyError, lambda: self.stuf.test3.setdefault('r', 8))
        self.assertEqual(self.stuf.setdefault('test1', 8), 'test1')
        self.assertRaises(KeyError, lambda: self.stuf.setdefault('pow', 8))


class TestFrozenStuf(Base, unittest.TestCase):

    @property
    def _impone(self):
        from stuf import frozenstuf
        return frozenstuf

    def test__setattr__(self):
        self.assertRaises(AttributeError, setattr(self.stuf, 'max', 3))
        self.assertRaises(
            AttributeError, setattr(self.stuf, 'test1', 'test1again')
        )
        self.assertRaises(
            AttributeError, setattr(self.stuf.test3, 'e', 5)
        )

    def test__setitem__(self):
        self.assertRaises(
            AttributeError, lambda: self.stuf.__setitem__('max', 3)
        )
        self.assertRaises(
            AttributeError,
            lambda: self.stuf.__setitem__('test2', 'test2again'),
        )
        self.assertRaises(
            AttributeError, lambda: self.stuf.test3.__setitem__('e', 5)
        )

    def test__delattr__(self):
        self.assertRaises(TypeError, lambda: delattr(self.stuf.test1))
        self.assertRaises(TypeError, lambda: delattr(self.stuf.test3.e))

    def test__delitem__(self):
        self.assertRaises(
            AttributeError, lambda: self.stuf.__delitem__('test1'),
        )
        self.assertRaises(
            AttributeError, lambda: self.stuf.test3.__delitem__('test1'),
        )

    def test_clear(self):
        self.assertRaises(AttributeError, lambda: self.stuf.test3.clear())
        self.assertRaises(AttributeError, lambda: self.stuf.clear())

    def test_pop(self):
        self.assertRaises(AttributeError, lambda: self.stuf.test3.pop('e'))
        self.assertRaises(AttributeError, lambda: self.stuf.pop('test1'))

    def test_popitem(self):
        self.assertRaises(AttributeError, lambda: self.stuf.test3.popitem())
        self.assertRaises(AttributeError, lambda: self.stuf.popitem())

    def test_setdefault(self):
        self.assertRaises(
            AttributeError, lambda: self.stuf.test3.setdefault('e', 8)
        )
        self.assertRaises(
            AttributeError, lambda: self.stuf.test3.setdefault('r', 8)
        )
        self.assertRaises(
            AttributeError, lambda: self.stuf.setdefault('test1', 8)
        )
        self.assertRaises(
            AttributeError, lambda: self.stuf.setdefault('pow', 8)
        )

    def test_update(self):
        tstuff = self._makeone
        self.assertRaises(
            AttributeError, lambda: self.stuf.test3.update(tstuff),
        )
        self.assertRaises(AttributeError, lambda: self.stuf.update(tstuff))


class TestOrderedStuf(Base, unittest.TestCase):

    @property
    def _impone(self):
        from stuf import orderedstuf
        return orderedstuf

    def test_reversed(self):
        slist = list(reversed(self.stuf))
        self.assertIn('test1', slist)
        self.assertIn('test2', slist)
        self.assertIn('test3', slist)

    def test_order(self):
        ostuf = self._impone([('a', 1), ('b', 2), ('c', 3), ('d', 4)])
        self.assertEqual(list(ostuf.items()), [('a', 1), ('b', 2), ('c', 3), ('d', 4)])

    def test_fromkeys(self):
        ostuf = self._impone.fromkeys(['a', 'b', 'c', 'd'], 1)
        self.assertEqual(list(ostuf.items()), [('a', 1), ('b', 1), ('c', 1), ('d', 1)])


class TestChainStuf(Base, unittest.TestCase):

    @property
    def _impone(self):
        from stuf.core import chainstuf
        return chainstuf

    @property
    def _makeone(self):
        return self._impone(
            dict(test1='test1'), dict(test2='test2'), dict(test3=dict(e=1))
        )

    def test_nofile(self):
        import sys
        s = self._impone(dict(a=sys.stdout), dict(b=1))
        self.assertEqual(s.a, sys.stdout)
        t = self._impone(dict(a=[sys.stdout]), dict(b=1))
        self.assertEqual(t.a, [sys.stdout])

    def test_clear(self):
        self.stuf.clear()
        self.assertEqual(len(self.stuf), 2)

    def test_pop(self):
        self.assertEqual(self.stuf.test3.pop('e'), 1)
        self.assertEqual(self.stuf.pop('test1'), 'test1')
        self.assertRaises(KeyError, lambda: self.stuf.pop('test2'))
        self.assertRaises(KeyError, lambda: self.stuf.pop('test3'))

    def test__delattr__(self):
        del self.stuf.test1
        self.assertRaises(AttributeError, lambda: delattr(self.stuf, 'test2'))
        self.assertRaises(AttributeError, lambda: delattr(self.stuf, 'test3'))
        self.assertRaises(AttributeError, lambda: delattr(self.stuf, 'test4'))
        self.assertEqual(len(self.stuf), 2)
        self.assertRaises(AttributeError, lambda: self.stuf.test1)
        self.assertEqual(self.stuf.test2, 'test2')
        self.assertEqual(dict(e=1), self.stuf.test3)
        self.assertEqual(1, self.stuf.test3.e)

    def test__delitem__(self):
        from operator import delitem
        del self.stuf['test1']
        self.assertRaises(KeyError, lambda: delitem(self.stuf, 'test2'))
        self.assertRaises(KeyError, lambda: delitem(self.stuf, 'test3'))
        self.assertEqual(len(self.stuf), 2)
        self.assertNotIn('test1', self.stuf)
        self.assertIn('test2', self.stuf)
        self.assertIn('test3', self.stuf)

    def test_parents(self):
        stuffed = self.stuf.parents
        self.assertEquals(
            stuffed.maps, [dict(test2='test2'), dict(test3=dict(e=1))]
        )

    def test_new_child(self):
        from stuf.core import stuf
        stuffed = self.stuf.new_child()
        self.assertEquals(
            stuffed.maps,
            [stuf(), stuf([('test1', 'test1')]), stuf(test2='test2'),
             stuf(test3=stuf(e=1))],
        )


class TestCounter(unittest.TestCase):

    @property
    def _impone(self):
        from stuf.core import countstuf
        return countstuf

    @property
    def _makeone(self):
        return self._impone(['test1', 'test2', 'test3'])

    def setUp(self):
        self.stuf = self._makeone

    def test__getattr__(self):
        self.assertEqual(self.stuf.test1, 1)
        self.assertEqual(self.stuf.test2, 1)
        self.assertEqual(self.stuf.test3, 1)

    def test__getitem__(self):
        self.assertEqual(self.stuf['test1'], 1)
        self.assertEqual(self.stuf['test2'], 1)
        self.assertEqual(self.stuf['test3'], 1)

    def test_get(self):
        self.assertEqual(self.stuf.get('test1'), 1)
        self.assertEqual(self.stuf.get('test2'), 1)
        self.assertIsNone(self.stuf.get('test4'), 1)
        self.assertEqual(self.stuf.get('test3'), 1)

    def test__setattr__(self):
        self.stuf.max = 3
        self.stuf.test1 = 'test1again'
        self.stuf.test2 = 'test2again'
        self.stuf.test3 = 5
        self.assertEqual(self.stuf.max, 3)
        self.assertEqual(self.stuf.test1, 'test1again')
        self.assertEqual(self.stuf.test2, 'test2again')
        self.assertEqual(self.stuf.test3, 5)

    def test__setitem__(self):
        self.stuf['max'] = 3
        self.stuf['test1'] = 'test1again'
        self.stuf['test2'] = 'test2again'
        self.stuf['test3'] = 5
        self.assertEqual(self.stuf['max'], 3)
        self.assertEqual(self.stuf['test1'], 'test1again')
        self.assertEqual(self.stuf['test2'], 'test2again')
        self.assertEqual(self.stuf['test3'], 5)

    def test__delattr__(self):
        del self.stuf.test1
        del self.stuf.test2
        del self.stuf.test3
        self.assertEqual(len(self.stuf), 0)

    def test__delitem__(self):
        del self.stuf['test1']
        del self.stuf['test2']
        del self.stuf['test3']
        self.assertEqual(len(self.stuf), 0)
        self.assertNotIn('test1', self.stuf)
        self.assertNotIn('test2', self.stuf)
        self.assertNotIn('test3', self.stuf)

    def test__cmp__(self):
        tstuff = self._makeone
        self.assertEqual(self.stuf, tstuff)

    def test__len__(self):
        self.assertEqual(len(self.stuf), 3)

    def test_repr(self):
        from stuf.six import strings
        self.assertIsInstance(repr(self._makeone), strings)
        self.assertIsInstance(repr(self.stuf), strings)

    def test_items(self):
        slist = list(self.stuf.items())
        self.assertIn(('test1', 1), slist)
        self.assertIn(('test2', 1), slist)
        self.assertIn(('test3', 1), slist)

    def test_iteritems(self):
        slist = list(self.stuf.iteritems())
        self.assertIn(('test1', 1), slist)
        self.assertIn(('test2', 1), slist)
        self.assertIn(('test3', 1), slist)

    def test_iter(self):
        slist = list(self.stuf)
        self.assertIn('test1', slist)
        self.assertIn('test2', slist)
        self.assertIn('test3', slist)

    def test_iterkeys(self):
        slist = list(self.stuf.iterkeys())
        self.assertIn('test1', slist)
        self.assertIn('test2', slist)
        self.assertIn('test3', slist)

    def test_itervalues(self):
        slist = list(self.stuf.itervalues())
        self.assertIn(1, slist)
        self.assertIn(1, slist)
        self.assertIn(1, slist)

    def test_values(self):
        slist2 = self.stuf.values()
        self.assertIn(1, slist2)
        self.assertIn(1, slist2)
        self.assertIn(1, slist2)

    def test_keys(self):
        slist2 = self.stuf.keys()
        self.assertIn('test1', slist2)
        self.assertIn('test2', slist2)
        self.assertIn('test3', slist2)

    def test_pickle(self):
        import pickle
        tstuf = self._makeone
        pkle = pickle.dumps(tstuf)
        nstuf = pickle.loads(pkle)
        self.assertIsInstance(nstuf, self._impone)
        self.assertEqual(tstuf, nstuf)

    def test_clear(self):
        self.stuf.clear()
        self.assertEqual(len(self.stuf), 0)

    def test_pop(self):
        self.assertEqual(self.stuf.pop('test1'), 1)
        self.assertEqual(self.stuf.pop('test2'), 1)
        self.assertEqual(self.stuf.pop('test3'), 1)

    def test_copy(self):
        tstuf = self._makeone
        nstuf = tstuf.copy()
        self.assertIsInstance(nstuf, self._impone)
        self.assertIsInstance(tstuf, self._impone)
        self.assertEqual(tstuf, nstuf)

    def test_popitem(self):
        item = self.stuf.popitem()
        self.assertEqual(len(item) + len(self.stuf), 4, item)

    def test_setdefault(self):
        self.assertEqual(self.stuf.setdefault('test1', 8), 1)
        self.assertEqual(self.stuf.setdefault('pow', 8), 8)

    def test_update(self):
        tstuff = self._makeone
        tstuff['test1'] = 3
        tstuff['test2'] = 6
        tstuff['test3'] = 2
        self.stuf.update(tstuff)
        self.assertEqual(self.stuf['test1'], 4)
        self.assertEqual(self.stuf['test2'], 7)
        self.assertEqual(self.stuf['test3'], 3)

    def test_basics(self):
        from stuf.utils import lrange
        c = self._impone('abcaba')
        self.assertEqual(c.most_common(), [('a', 3), ('b', 2), ('c', 1)])
        for i in lrange(5):
            self.assertEqual(
                c.most_common(i), [('a', 3), ('b', 2), ('c', 1)][:i]
            )
        self.assertEqual(''.join(sorted(c.elements())), 'aaabbc')
        c.a += 1         # increment an existing value
        c.b -= 2         # sub existing value to zero
        del c.c          # remove an entry
        del c.c          # make sure that del doesn't raise KeyError
        c.d -= 2         # sub from a missing value
        c.e = -5         # directly assign a missing value
        c.f += 4         # add to a missing value

    def test_copy_subclass(self):
        class MyCounter(self._impone):
            pass
        c = MyCounter('slartibartfast')
        d = c.copy()
        self.assertEqual(d, c)
        self.assertEqual(len(d), len(c))
        self.assertEqual(type(d), type(c))

    def test_invariant_for_the_in_operator(self):
        c = self._impone(a=10, b=-2, c=0)
        for elem in c:
            self.assertTrue(elem in c)
            self.assertIn(elem, c)

    def test_multiset_operations(self):
        from stuf.utils import lrange
        from random import randrange
        # Verify that adding a zero counter will strip zeros and negatives
        c = self._impone(a=10, b=-2, c=0) + self._impone()
        self.assertEqual(dict(c), dict(a=10))
        elements = 'abcd'
        for _ in lrange(1000):
            # test random pairs of multisets
            p = self._impone(
                dict((elem, randrange(-2, 4)) for elem in elements))
            p.update(e=1, f=-1, g=0)
            q = self._impone(
                dict((elem, randrange(-2, 4)) for elem in elements))
            q.update(h=1, i=-1, j=0)
            for counterop, numberop in [
                (self._impone.__add__, lambda x, y: max(0, x + y)),
                (self._impone.__sub__, lambda x, y: max(0, x - y)),
                (self._impone.__or__, lambda x, y: max(0, x, y)),
                (self._impone.__and__, lambda x, y: max(0, min(x, y))),
            ]:
                result = counterop(p, q)
                for x in elements:
                    self.assertEqual(numberop(p[x], q[x]), result[x],
                                     (counterop, x, p, q))
                # verify that results exclude non-positive counts
                self.assertTrue(x > 0 for x in result.values())
        elements = 'abcdef'
        for _ in lrange(100):
            # verify that random multisets with no repeats are exactly like sets
            p = self._impone(
                dict((elem, randrange(0, 2)) for elem in elements))
            q = self._impone(
                dict((elem, randrange(0, 2)) for elem in elements))
            for counterop, setop in [
                (self._impone.__sub__, set.__sub__),
                (self._impone.__or__, set.__or__),
                (self._impone.__and__, set.__and__),
            ]:
                counter_result = counterop(p, q)
                set_result = setop(set(p.elements()), set(q.elements()))
                self.assertEqual(counter_result, dict.fromkeys(set_result, 1))

    def test_unary(self):
        c = self._impone(a=-5, b=0, c=5, d=10, e=15, g=40)
        self.assertEqual(dict(+c), dict(c=5, d=10, e=15, g=40))
        self.assertEqual(dict(-c), dict(a=5))

    def test_repr_nonsortable(self):
        c = self._impone(a=2, b=None)
        r = repr(c)
        self.assertEqual("countstuf(a=2, b=None)", r)

    def test_subtract(self):
        c = self._impone(a=-5, b=0, c=5, d=10, e=15, g=40)
        c.subtract(a=1, b=2, c=-3, d=10, e=20, f=30, h=-50)
        self.assertEqual(
            c, self._impone(a=-6, b=-2, c=8, d=0, e=-5, f=-30, g=40, h=50))
        c = self._impone(a=-5, b=0, c=5, d=10, e=15, g=40)
        c.subtract(self._impone(a=1, b=2, c=-3, d=10, e=20, f=30, h=-50))
        self.assertEqual(
            c, self._impone(a=-6, b=-2, c=8, d=0, e=-5, f=-30, g=40, h=50))
        c = self._impone('aaabbcd')
        c.subtract('aaaabbcce')
        self.assertEqual(c, self._impone(a=-1, b=0, c=-1, d=1, e=-1))


if __name__ == '__main__':
    unittest.main()

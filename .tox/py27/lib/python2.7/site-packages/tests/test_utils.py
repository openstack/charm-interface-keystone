# -*- coding: utf-8 -*-
'''stuf utility tests'''

from stuf.six import unittest


class TestUtils(unittest.TestCase):

    def test_attr_or_item(self):
        from collections import namedtuple
        from stuf.deep import attr_or_item
        Test = namedtuple('Test', 'a')
        foo = Test(a=2)
        foo2 = dict(a=2)
        self.assertEqual(attr_or_item(foo, 'a'), attr_or_item(foo2, 'a'))

    def test_setdefault(self):
        from stuf import stuf
        from stuf.deep import setdefault
        foo = stuf(a=1)
        self.assertEqual(setdefault(foo, 'a', 1), 1)
        self.assertEqual(setdefault(foo, 'b', 2), 2)

    def test_clsname(self):
        from stuf import stuf
        from stuf.deep import clsname
        foo = stuf(a=2)
        self.assertEqual(clsname(foo), 'stuf')

    def test_deepget(self):
        from stuf import stuf
        from stuf.deep import deepget
        foo = stuf(a=stuf(b=(stuf(f=stuf(g=1)))))
        self.assertEqual(deepget(foo, 'a.b.f.g'), 1)
        self.assertEqual(deepget(foo, 'a.b.f.e'), None)

    def test_deleter(self):
        from stuf import stuf
        from stuf.deep import deleter
        foo = stuf(a=1)
        self.assertEqual(deleter(foo, 'a'), None)

    def test_getcls(self):
        from stuf import stuf
        from stuf.deep import getcls
        foo = stuf(a=1)
        self.assertEqual(getcls(foo), stuf)

    def test_getter(self):
        from stuf import stuf
        from stuf.deep import getter
        foo = stuf(a=1)
        self.assertEqual(getter(foo, 'a'), 1)
        self.assertEqual(getter(stuf, 'items'), stuf.items)

    def test_selfname(self):
        from stuf.deep import selfname
        class Foo(object): #@IgnorePep8
            pass
        class Foo2: #@IgnorePep8
            pass
        self.assertEqual(selfname(Foo), 'Foo')
        self.assertEqual(selfname(Foo2), 'Foo2')

    def test_setter(self):
        from stuf.deep import setter
        class Foo(object): #@IgnorePep8
            pass
        foo = Foo()
        self.assertEqual(setter(Foo, 'a', 1), 1)
        self.assertEqual(setter(foo, 'b', 1), 1)

    def test_deferfunc(self):
        from stuf.six import next
        from stuf.iterable import deferfunc
        deferred = deferfunc(lambda: 1)
        self.assertEqual(next(deferred), 1)

    def test_deferiter(self):
        from stuf.six import next
        from stuf.iterable import deferiter
        deferred = deferiter(iter([1, 2, 3]))
        self.assertEqual(next(deferred), 1)

    def test_count(self):
        from stuf.iterable import count
        self.assertEqual(count([1, 2, 3]), 3)

    def test_breakcount(self):
        from stuf.six import next
        from functools import partial
        from stuf.iterable import breakcount
        deferred = breakcount(partial(next, iter([1, 2, 3])), 2)
        self.assertEqual(list(deferred), [1, 2])

    def test_iterexcept(self):
        from stuf.six import next
        from functools import partial
        from stuf.iterable import iterexcept
        deferred = iterexcept(
            partial(next, iter([1, 2, 3])), StopIteration, lambda: 1,
        )
        self.assertEqual(list(deferred), [1, 1, 2, 3])

    def test_exhaustmap(self):
        from stuf import exhaustmap
        deferred = exhaustmap(lambda x: x + x, iter([1, 2, 3]), StopIteration)
        self.assertIsNone(deferred)

    def test_exhauststar(self):
        from stuf.iterable import exhauststar
        deferred = exhauststar(lambda x, y: x + y, iter([(1, 2), (3, 4)]))
        self.assertIsNone(deferred)

    def test_exhaustitems(self):
        from stuf import exhaustitems
        deferred = exhaustitems(lambda x, y: x + y, {1: 2})
        self.assertIsNone(deferred)

    def test_lazy_class(self):
        from stuf.desc import lazy_class
        class Foo(object): #@IgnorePep8
            @lazy_class
            def this(self):
                return self
        self.assertEqual(Foo, Foo.this)

    def test_lazy_set(self):
        from stuf.desc import lazyset
        class Foo(object): #@IgnorePep8
            @lazyset
            def this(self):
                return self._foo + 1
            @this.setter #@IgnorePep8
            def this(self, this):
                self._foo = this
        foo = Foo()
        foo.this = 1
        self.assertEqual(foo.this, 2)
        del foo.this

    def test_twoway(self):
        from stuf.desc import twoway
        class Foo(object): #@IgnorePep8
            @twoway
            def this(self):
                return 1
            @this.expression #@IgnorePep8
            def this(self):
                return 2
        self.assertEqual(Foo.this, 2)
        foo = Foo()
        self.assertEqual(foo.this, 1)

    def test_either(self):
        from stuf.desc import either
        class Foo(object): #@IgnorePep8
            @either
            def this(self):
                return 1
            @this.expression #@IgnorePep8
            def this(self):
                return 2
        self.assertEqual(Foo.this, 2)
        foo = Foo()
        self.assertEqual(foo.this, 2)

    def test_both(self):
        from stuf.desc import both
        class Foo(object): #@IgnorePep8
            @both
            def this(self):
                return 1
            @this.expression #@IgnorePep8
            def this(self):
                return 2
        self.assertEqual(Foo.this, 2)
        foo = Foo()
        self.assertEqual(foo.this, 1)

    def test_lazyimport(self):
        from stuf.six import callable
        from stuf.utils import lazyimport
        fsum = lazyimport('math.fsum')
        self.assertTrue(callable(fsum))
        fsum = lazyimport('math', 'fsum')
        self.assertTrue(callable(fsum))

    def test_checkname(self):
        from stuf.base import checkname
        self.assertEqual(checkname('from'), 'from_')

    def test_sluggify(self):
        from stuf.utils import sluggify
        self.assertEqual(sluggify('This is a slug'), 'this-is-a-slug')

    def test_lru(self):
        from stuf.utils import lru, sluggify
        slug = lru(2)(sluggify)
        self.assertEqual(slug('This is a slug'), 'this-is-a-slug')
        self.assertEqual(slug('This is a plug'), 'this-is-a-plug')
        self.assertEqual(slug('This is a flug'), 'this-is-a-flug')
        self.assertEqual(slug('This is a dug'), 'this-is-a-dug')
        self.assertEqual(slug('This is a slug'), 'this-is-a-slug')
        self.assertEqual(slug('This is a plug'), 'this-is-a-plug')
        self.assertEqual(slug('This is a flug'), 'this-is-a-flug')
        self.assertEqual(slug('This is a dug'), 'this-is-a-dug')
        slug = lru(None)(sluggify)
        self.assertEqual(slug('This is a slug'), 'this-is-a-slug')
        self.assertEqual(slug('This is a plug'), 'this-is-a-plug')
        self.assertEqual(slug('This is a flug'), 'this-is-a-flug')
        self.assertEqual(slug('This is a slug'), 'this-is-a-slug')
        self.assertEqual(slug('This is a plug'), 'this-is-a-plug')
        self.assertEqual(slug('This is a dug'), 'this-is-a-dug')

    def test_ascii(self):
        from stuf.six import u, b, tobytes
        self.assertEqual(
[tobytes(i, 'ascii') for i in [[1], True, r't', b('i'), u('g'), None, (1,)]],
[b('[1]'), b('True'), b('t'), b('i'), b('g'), b('None'), b('(1,)')]
        )

    def test_bytes(self):
        from stuf.six import u, b, tobytes
        self.assertEqual(
            [tobytes(i) for i in [[1], True, r't', b('i'), u('g'), None, (1,)]],
            [b('[1]'), b('True'), b('t'), b('i'), b('g'), b('None'), b('(1,)')]
        )

    def test_unicode(self):
        from stuf.six import u, b, tounicode
        self.assertEqual(
        [tounicode(i) for i in [[1], True, r't', b('i'), u('g'), None, (1,)]],
        [u('[1]'), u('True'), u('t'), u('i'), u('g'), u('None'), u('(1,)')]
        )



if __name__ == '__main__':
    unittest.main()

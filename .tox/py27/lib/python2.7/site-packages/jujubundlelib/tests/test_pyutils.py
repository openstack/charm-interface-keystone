# Copyright 2015 Canonical Ltd.
# Licensed under the AGPLv3, see LICENCE file for details.

from __future__ import unicode_literals

import unittest

from jujubundlelib import pyutils


class TestStringClass(unittest.TestCase):

    @unittest.skipIf(pyutils.PY3, 'only run under Python 2')
    def test_python2(self):
        cls = type(b'Example', (object,), {'__str__': lambda self: 'example'})
        instance = pyutils.string_class(cls)()
        byte_string = str(instance)
        self.assertIsInstance(byte_string, bytes)
        self.assertEqual(b'example', byte_string)
        unicode_string = unicode(instance)
        self.assertNotIsInstance(unicode_string, bytes)
        self.assertEqual('example', unicode_string)

    @unittest.skipUnless(pyutils.PY3, 'only run under Python 3')
    def test_python3(self):
        cls = type('Example', (), {'__str__': lambda self: 'example'})
        instance = pyutils.string_class(cls)()
        unicode_string = str(instance)
        self.assertIsInstance(unicode_string, str)
        self.assertEqual('example', unicode_string)
        with self.assertRaises(AttributeError):
            self.instance.__unicode__()

    @unittest.skipIf(pyutils.PY3, 'only run under Python 2')
    def test_error(self):
        non_string_class = type(b'ExampleNonString', (object,), {})
        with self.assertRaises(TypeError) as ctx:
            pyutils.string_class(non_string_class)
        self.assertEqual(
            'the given class has no __str__ method', str(ctx.exception))


class TestExceptionString(unittest.TestCase):

    def test_exception_string(self):
        msg = 'bad-wolf'
        e = ValueError(msg.encode('utf-8'))
        message = pyutils.exception_string(e)
        self.assertNotIsInstance(message, bytes)
        self.assertEqual('bad-wolf', message)

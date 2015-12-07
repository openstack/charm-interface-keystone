# Copyright 2015 Canonical Ltd.
# Licensed under the AGPLv3, see LICENCE file for details.

from __future__ import unicode_literals

import collections
import unittest

from jujubundlelib import typeutils


class TestIsdict(unittest.TestCase):

    def test_dict(self):
        for value in ({}, collections.OrderedDict()):
            self.assertTrue(typeutils.isdict(value), str(value))

    def test_non_dict(self):
        for value in ('', [1, 2], 42, None, object()):
            self.assertFalse(typeutils.isdict(value), str(value))


class TestIslist(unittest.TestCase):

    def test_list(self):
        tests = (
            [1, 2],
            (),
            ('foo', 'bar'),
            collections.namedtuple('Test', 'test')('test'),
        )
        for value in tests:
            self.assertTrue(typeutils.islist(value), str(value))

    def test_non_list(self):
        for value in ('', {}, 42, None, object()):
            self.assertFalse(typeutils.islist(value), str(value))


class TestIsstring(unittest.TestCase):

    def test_string(self):
        for value in ('', 'foo', b'bar'):
            self.assertTrue(typeutils.isstring(value), str(value))

    def test_non_string(self):
        for value in ([1, 2], {}, 42, None, object()):
            self.assertFalse(typeutils.isstring(value), str(value))

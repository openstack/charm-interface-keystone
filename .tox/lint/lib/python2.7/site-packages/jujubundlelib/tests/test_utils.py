# Copyright 2015 Canonical Ltd.
# Licensed under the AGPLv3, see LICENCE file for details.

from __future__ import unicode_literals

import unittest

from jujubundlelib import utils


class TestUtils(unittest.TestCase):

    def test_is_legacy_bundle(self):
        self.assertTrue(utils.is_legacy_bundle({'services': {}}))
        self.assertFalse(utils.is_legacy_bundle({
            'services': {},
            'machines': {},
        }))

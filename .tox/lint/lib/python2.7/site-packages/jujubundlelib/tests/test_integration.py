# Copyright 2015 Canonical Ltd.
# Licensed under the AGPLv3, see LICENCE file for details.

from __future__ import (
    print_function,
    unicode_literals,
)

import json
import os
import pprint
import traceback
import unittest
try:
    from urllib.request import (
        HTTPError,
        urlopen,
    )
except ImportError:
    from urllib2 import (
        HTTPError,
        urlopen,
    )

import yaml

from jujubundlelib import (
    changeset,
    references,
    validation,
)


# Define the URL to the charm store API.
CHARMSTORE_URL = 'https://api.jujucharms.com/charmstore/v4/'
# Define the name of the environment variable used to run the functional tests.
FTEST_ENV_VAR = 'JUJU_BUNDLELIB_FTESTS'


def get_references():
    """Retrieve the bundle references from the charm store."""
    response = urlopen(CHARMSTORE_URL + 'search?series=bundle&limit=10000')
    content = response.read().decode('utf-8')
    data = json.loads(content)
    for result in data['Results']:
        yield references.Reference.from_fully_qualified_url(result['Id'])


def get_bundle(reference):
    """Retrieve the bundle content for the given reference from the store."""
    response = urlopen(
        CHARMSTORE_URL + reference.path() + '/archive/bundle.yaml')
    return yaml.load(response)


skip_if_ftests_disabled = unittest.skipUnless(
    os.getenv(FTEST_ENV_VAR) == '1',
    'to run functional tests, set {} to "1"'.format(FTEST_ENV_VAR))


@skip_if_ftests_disabled
class TestFunctional(unittest.TestCase):

    def setUp(self):
        # Collect bundles from the charm store.
        self.references = get_references()

    def test_bundle(self):
        # All the charm store bundles pass validation.
        # It is possible to get the change set corresponding to each bundle.
        # This test ensures there are no false positives when validating a
        # bundle: charm store bundles are assumed to be valid.
        # Note that this test requires network connection.
        for ref in self.references:
            try:
                bundle = get_bundle(ref)
            except HTTPError as err:
                print('skipping {}: {}'.format(ref, err))
                continue
            # Check bundle validation.
            errors = validation.validate(bundle)
            self.assertEqual(
                [], errors,
                'ref: {}\n{}\nerrors: {}'.format(
                    ref, pprint.pformat(bundle), errors))
            # Check change set generation.
            try:
                changes = list(changeset.parse(bundle))
            except:
                msg = 'changeset parsing error\nref: {}\n{}\n{}'.format(
                    ref, pprint.pformat(bundle), traceback.format_exc())
                self.fail(msg)
            self.assertTrue(changes)

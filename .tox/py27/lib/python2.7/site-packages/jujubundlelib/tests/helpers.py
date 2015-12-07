# Copyright 2015 Canonical Ltd.
# Licensed under the AGPLv3, see LICENCE file for details.

from __future__ import unicode_literals

from contextlib import contextmanager
import os
import tempfile

import mock
import yaml

from jujubundlelib import pyutils


class BundleFileTestsMixin(object):
    """Shared methods for testing Juju bundle files."""

    bundle_data = {
        'series': 'precise',
        'services': {
            'wordpress': {
                'charm': 'cs:trusty/wordpress-42',
                'num_units': 1,
            },
            'mysql': {
                'charm': 'cs:trusty/mysql-47',
                'num_units': 0,
            },
        },
        'machines': {},
    }
    bundle_content = yaml.safe_dump(bundle_data)

    def make_bundle_file(self, content=None):
        """Create a Juju bundle file containing the given contents.

        If content is None, use the valid bundle contents defined in
        self.bundle_content.
        Return the bundle file path.
        """
        bundle_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        self.addCleanup(os.remove, bundle_file.name)
        if content is None:
            content = self.bundle_content
        elif isinstance(content, dict):
            content = yaml.safe_dump(content)
        bundle_file.write(content.encode('utf-8'))
        bundle_file.close()
        return bundle_file.name


def mock_print():
    """Mock the builtin print function."""
    if pyutils.PY3:
        return mock.patch('builtins.print')
    return mock.patch('__builtin__.print')


class ValueErrorTestsMixin(object):
    """Set up some base methods for testing functions raising ValueErrors."""

    @contextmanager
    def assert_value_error(self, error, message=None):
        """Ensure a ValueError is raised in the context block.

        Also check that the exception includes the expected error message.
        """
        with self.assertRaises(ValueError) as context_manager:
            yield
        self.assertEqual(error, context_manager.exception.args[0], message)

# Copyright 2015 Canonical Ltd.
# Licensed under the AGPLv3, see LICENCE file for details.

from __future__ import unicode_literals


def is_legacy_bundle(bundle):
    """Report whether the bundle uses the legacy (version 3) syntax."""
    return 'machines' not in bundle

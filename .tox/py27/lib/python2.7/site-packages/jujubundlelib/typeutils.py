# Copyright 2015 Canonical Ltd.
# Licensed under the AGPLv3, see LICENCE file for details.

from __future__ import unicode_literals

import collections

from jujubundlelib import pyutils


def isdict(value):
    """Report whether the given value is a dict-like object."""
    return isinstance(value, collections.Mapping)


def islist(value):
    """Report whether the given value is a sequence."""
    return isinstance(value, (list, tuple))


def isstring(value):
    """Report whether the given value is a byte or unicode string."""
    classes = (str, bytes) if pyutils.PY3 else basestring
    return isinstance(value, classes)

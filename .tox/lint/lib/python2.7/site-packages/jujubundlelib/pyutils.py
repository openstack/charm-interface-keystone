# Copyright 2015 Canonical Ltd.
# Licensed under the AGPLv3, see LICENCE file for details.

import sys


# Report whether we are using Python 3 or Python 2.
PY3 = sys.version_info >= (3, 0)


def string_class(cls):
    """Define __unicode__ and __str__ methods on the given class in Python 2.

    The given class must define a __str__ method returning a unicode string,
    otherwise a TypeError is raised.
    Under Python 3, the class is returned as is.
    """
    if not PY3:
        if '__str__' not in cls.__dict__:
            raise TypeError('the given class has no __str__ method')
        cls.__unicode__, cls.__string__ = (
            cls.__str__, lambda self: self.__unicode__().encode('utf-8'))
    return cls


def exception_string(exception):
    """Return the string value of an exception, valid for both python 2 and
    python 3.
    """
    return exception.args[0].decode('utf-8')

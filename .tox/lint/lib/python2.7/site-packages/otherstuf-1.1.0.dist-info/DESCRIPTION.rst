| |version| |downloads| |versions| |impls| |wheel| |coverage|

.. |version| image:: http://img.shields.io/pypi/v/otherstuf.svg?style=flat
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/otherstuf

.. |downloads| image:: http://img.shields.io/pypi/dm/otherstuf.svg?style=flat
    :alt: PyPI Package monthly downloads
    :target: https://pypi.python.org/pypi/otherstuf

.. |versions| image:: https://img.shields.io/pypi/pyversions/otherstuf.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/otherstuf

.. |impls| image:: https://img.shields.io/pypi/implementation/otherstuf.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/otherstuf

.. |wheel| image:: https://img.shields.io/pypi/wheel/otherstuf.svg
    :alt: Wheel packaging support
    :target: https://pypi.python.org/pypi/otherstuf

.. |coverage| image:: https://img.shields.io/badge/test_coverage-100%25-6600CC.svg
    :alt: Test line coverage
    :target: https://pypi.python.org/pypi/otherstuf

Attribute-accesible collections inspired by `stuf
<http://pypi.python.org/pypi/stuf>`_. Implements ``chainstuf`` and
``counterstuf``: versions of ``ChainMap`` and ``Counter`` that expose their keys as
attributes.

The ultimate goal of this module is to have these functions available in the
``stuf`` module, and this sidecar to be retired.

Usage
=====

Use these just like you would ``ChainMap`` and ``Counter``, except that
you get attribute-style access as well.

For ``chainstuf``::

    from otherstuf import chainstuf

    d1 = dict(this=1, that=2)
    d2 = dict(roger=99, that=100)

    # test simple attribute equivalence
    c = chainstuf(d1, d2)

    assert c.this == 1
    assert c.roger == 99

    c.roger = 'wilco'
    assert c.roger
    print "roger", c.roger

    d1.update(feeling='fancypants!')
    print "i'm feeling", c.feeling     # passed through, since d2 lacks 'feeling'

Given recent versions (e.g. beyond 0.9.10) of ``stuf``, one could simply use
``from stuf import chainstuf``. This portion of the ``otherstuf``
sidecar is now superfluous.

For ``counterstuf``::

    from otherstuf import counterstuf

    c = counterstuf()
    c.update("this and this is this but that isn't this".split())
    c.total = sum(c.values())

    print "everything:", c.total
    print "'this' mentioned", c.this, "times"
    print "'bozo' mentioned", c.bozo, "times"
    print c

Notes
=====

* Version 1.1.0 initates automated test coverage metrics. Test coverage
  started at 88%. Cleanups got coverage to 100%. *Hooah!*

* Automated multi-version testing managed with `pytest
  <http://pypi.python.org/pypi/pytest>`_, `pytest-cov
  <http://pypi.python.org/pypi/pytest-cov>`_,
  `coverage <https://pypi.python.org/pypi/coverage/4.0b1>`_
  and `tox
  <http://pypi.python.org/pypi/tox>`_.
  Packaging linting with `pyroma <https://pypi.python.org/pypi/pyroma>`_.

  Successfully packaged for, and
  tested against, all late-model versions of Python: 2.6, 2.7, 3.2, 3.3,
  3.4, and 3.5 pre-release (3.5.0b3) as well as PyPy 2.6.0 (based on
  2.7.9) and PyPy3 2.4.0 (based on 3.2.5). Test line coverage 100%.

* As of 1.0.0, updated to use semantic versioning and
  the Apache Software License.

* Recent builds of ``stuf`` have left Python 2.6 out in
  the cold. This package requires ``stuf==0.9.14`` for 2.6--the
  last version to successfully install there. Newer Python
  releases will get ``stuf>=0.9.16``. I've submitted
  a patch for 2.6 installability to carry forward; we'll
  have to see where that goes.

* The author, `Jonathan Eunice <mailto:jonathan.eunice@gmail.com>`_ or
  `@jeunice on Twitter <http://twitter.com/jeunice>`_
  welcomes your comments and suggestions.

Installation
============

To install or upgrade to the latest version::

    pip install -U otherstuf

To ``easy_install`` under a specific Python version (3.3 in this example)::

    python3.3 -m easy_install --upgrade otherstuf

(You may need to prefix these with ``sudo`` to authorize
installation. In environments without super-user privileges, you may want to
use ``pip``'s ``--user`` option, to install only for a single user, rather
than system-wide.)


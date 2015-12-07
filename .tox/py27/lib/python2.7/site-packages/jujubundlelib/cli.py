# Copyright 2015 Canonical Ltd.
# Licensed under the AGPLv3, see LICENCE file for details.

from __future__ import (
    print_function,
    unicode_literals,
)

import argparse
import json
import sys

import yaml

import jujubundlelib
from jujubundlelib import (
    changeset,
    validation,
)


# Retrieve the application version.
version = jujubundlelib.get_version()


def get_changeset(args):
    """Dump the changeset objects as JSON, reading the provided bundle YAML.

    The YAML can be provided either from stdin or by passing a file path as
    first argument.
    """
    # Parse the arguments.
    parser = argparse.ArgumentParser(description=get_changeset.__doc__)
    parser.add_argument(
        'infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
        help='path to the bundle YAML file')
    parser.add_argument(
        '--version', action='version', version='%(prog)s {}'.format(version))
    options = parser.parse_args(args)

    # Parse the provided YAML file.
    try:
        bundle = yaml.safe_load(options.infile)
    except Exception:
        return 'error: the provided bundle is not a valid YAML'

    # Validate the bundle object.
    errors = validation.validate(bundle)
    if errors:
        return '\n'.join(errors)

    # Dump the changeset to stdout.
    print('[')
    for num, change in enumerate(changeset.parse(bundle)):
        if num:
            print(',')
        print(json.dumps(change))
    print(']')

import collections


# Define a sequence of allowed constraints to be used in the process of
# preparing the bundle object. See the _prepare_constraints function below.
ALLOWED_CONSTRAINTS = (
    'arch',
    'container',
    'cpu-cores',
    'cpu-power',
    'mem',
    'root-disk',
    'tags',
)


def parse_constraints(original_constraints):
    """Parse the constraints and validate them.

    constraints is a string of key=value pairs or a dict.  Due to
    historical reasons, many bundles use a comma-separated list rather
    than the space-separated list juju-core expects.  This method
    handles both separators.

    Returns a dict of validated constraints.
    Raises ValueError if one or more constraints is invalid.
    """

    constraints = original_constraints
    if not isinstance(constraints, collections.Mapping):
        constraints = constraints.strip()
        if not constraints:
            return {}
        num_equals = constraints.count('=')

        if 'tags' in constraints:
            # Tags are comma-separated and force the key,value pairs of the
            # constraints to be space-separated.
            pairs = constraints.split(' ')
        else:
            # Comma separation is supported but deprecated.  Attempt splitting
            # on it first as it yields better results if a mix of commas and
            # spaces is used.
            pairs = constraints.split(',')
        if num_equals != len(pairs):
            pairs = constraints.split(' ')
        if num_equals != len(pairs):
            raise ValueError('invalid constraints: {}'.format(
                original_constraints))

        constraints = {}
        for item in pairs:
            k, v = item.split('=')
            if v.find(',') != -1 and k != 'tags':
                raise ValueError('invalid constraints: {}'.format(
                    original_constraints))

            constraints[k.strip()] = v.strip()

    unsupported = set(constraints).difference(ALLOWED_CONSTRAINTS)
    if unsupported:
        msg = 'unsupported constraints: {}'.format(
            ', '.join(sorted(unsupported)))
        raise ValueError(msg)
    return constraints


def check_constraints(original_constraints):
    """Check to see that constraints are space-separated and valid."""
    try:
        parsed = parse_constraints(original_constraints)
    except ValueError:
        return False
    tokens = original_constraints.strip().split()
    return len(parsed) == len(tokens)

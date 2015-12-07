# Copyright 2015 Canonical Ltd.
# Licensed under the AGPLv3, see LICENCE file for details.

from __future__ import unicode_literals

import pprint

from jujubundlelib import validation


# Define validation tests as a dict mapping test names to tuples of type
# (expected_errors, bundle) where expected_errors is a list of the errors
# returned by validation.validate called passing the bundle content.
_validation_tests = {
    # Valid bundle.
    'test_valid_bundle': (
        [],
        {
            'services': {
                'django': {'charm': 'cs:trusty/django-42', 'num_units': 1},
            },
        },
    ),
    'test_valid_bundle_series': (
        [],
        {
            'series': 'precise',
            'services': {
                'django': {'charm': 'cs:trusty/django-42', 'num_units': 1},
            },
        },
    ),
    'test_valid_bundle_exposed': (
        [],
        {
            'series': 'wily',
            'services': {
                'django': {'charm': 'cs:trusty/django-42', 'expose': True},
            },
        },
    ),
    'test_valid_bundle_unexposed': (
        [],
        {
            'series': 'wily',
            'services': {
                'django': {'charm': 'cs:trusty/django-42', 'expose': False},
            },
        },
    ),
    'test_valid_bundle_machines': (
        [],
        {
            'services': {
                'django': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 1,
                    'to': ['1'],
                },
            },
            'machines': {1: {}},
        },
    ),
    'test_valid_bundle_machines_none': (
        [],
        {
            'services': {
                'django': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 1,
                    'to': ['1'],
                },
            },
            'machines': {1: None},
        },
    ),
    'test_valid_bundle_relations': (
        [],
        {
            'services': {
                'django': {'charm': 'cs:trusty/django-42', 'num_units': 1},
                'haproxy': {'charm': 'cs:trusty/haproxy-47', 'num_units': 0},
            },
            'relations': [('django:http', 'haproxy:http')],
        },
    ),
    'test_valid_bundle_all_sections': (
        [],
        {
            'series': 'precise',
            'services': {
                'django': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 1,
                    'to': ['1'],
                },
                'haproxy': {'charm': 'cs:trusty/haproxy-47', 'num_units': 0},
            },
            'machines': {1: {}},
            'relations': [('django:http', 'haproxy:http')],
        },
    ),
    'test_valid_bundle_partial_service_url': (
        [],
        {
            'services': {
                'django': {'charm': 'django', 'num_units': 1},
                'haproxy': {'charm': 'trusty/haproxy', 'num_units': 0},
            },
        },
    ),
    'test_valid_bundle_string_placement': (
        [],
        {
            'services': {
                'django': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 1,
                    'to': '0',
                },
            },
            'machines': {0: {}},
        },
    ),
    'test_valid_bundle_no_num_units': (
        [],
        {
            'services': {
                'django': {'charm': 'cs:trusty/django-42'},
            },
        },
    ),
    'test_valid_bundle_constraints': (
        [],
        {
            'services': {
                'django': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 1,
                    'constraints': 'cpu-cores=8 arch=amd64',
                },
            },
        },
    ),
    'test_valid_bundle_storage_constraints': (
        [],
        {
            'services': {
                'django': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 1,
                    'storage': {'data': 'ebs,10G', 'cache': 'ebs-ssd'},
                },
            },
        },
    ),
    'test_valid_bundle_options': (
        [],
        {
            'services': {
                'django': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 1,
                    'options': {'key1': 47, 'key2': 'val2'},
                },
            },
        },
    ),
    'test_valid_unit_placement': (
        [],
        {
            'services': {
                'django': {
                    'charm': 'trusty/django',
                    'num_units': 3,
                    'to': ['kvm:0', '1'],
                },
                'rails': {'charm': 'rails', 'num_units': 1},
                'haproxy': {
                    'charm': 'haproxy',
                    'num_units': 1,
                    'to': 'rails/0',
                },
                'memcached': {
                    'charm': 'cs:memcached-42',
                    'num_units': 2,
                    'to': ['lxc:1', 'new'],
                }
            },
            'machines': {
                '0': {
                    'series': 'trusty',
                    'constraints': 'mem=8000 cpu-cores=4',
                    'annotations': {
                        'foo': 'bar',
                    },
                },
                '1': {},
            },
        },
    ),
    'test_valid_service_placement_v4_bundle': (
        [],
        {
            'services': {
                'django': {
                    'charm': 'trusty/django',
                    'num_units': 1,
                    'to': ['kvm:2'],
                },
            },
            'machines': {
                '2': {'series': 'precise'},
            },
        },
    ),
    'test_valid_relations': (
        [],
        {
            'services': {
                'django': {
                    'charm': 'trusty/django',
                    'num_units': 3,
                    'to': ['kvm:0', '1'],
                },
                'rails': {'charm': 'rails', 'num_units': 1},
                'haproxy': {
                    'charm': 'haproxy',
                    'num_units': 1,
                    'to': 'rails/0',
                },
                'memcached': {
                    'charm': 'cs:memcached-42',
                    'num_units': 2,
                    'to': ['lxc:1', 'new'],
                }
            },
            'machines': {
                '0': {
                    'series': 'trusty',
                    'constraints': 'mem=8000 cpu-cores=4',
                    'annotations': {
                        'foo': 'bar',
                    },
                },
                '1': {},
            },
            'relations': [
                ['django:web', 'haproxy:web'],
                ['rails:cache', 'memcached:cache'],
                ['haproxy', 'rails'],
                ['django:cache', 'memcached'],
            ],
        },
    ),

    # Invalid bundle.
    'test_invalid_bundle_int': (
        ['bundle does not appear to be a bundle'],
        42,
    ),
    'test_invalid_bundle_string': (
        ['bundle does not appear to be a bundle'],
        'invalid',
    ),

    # Invalid bundle sections.
    'test_empty_bundle': (
        ['bundle does not define any services'],
        {},
    ),
    'test_no_services_section': (
        ['bundle does not define any services'],
        {'services': {}},
    ),
    'test_invalid_services_section': (
        ['services spec does not appear to be well-formed'],
        {'services': 42},
    ),
    'test_invalid_machines_section': (
        ['machines spec does not appear to be well-formed'],
        {
            'services': {
                'django': {'charm': 'cs:trusty/django-42', 'num_units': 1},
            },
            'machines': 42,
        },
    ),
    'test_invalid_machines_section_non_digit_string': (
        ['machines spec identifiers must be digits'],
        {
            'services': {
                'django': {'charm': 'cs:trusty/django-42', 'num_units': 1},
            },
            'machines': {'foo': {}},
        },
    ),
    'test_invalid_machines_section_non_digit_tuple': (
        ['machines spec identifiers must be digits'],
        {
            'services': {
                'django': {'charm': 'cs:trusty/django-42', 'num_units': 1},
            },
            'machines': {'1': {}, ('foo'): {}},
        },
    ),
    'test_invalid_relations_section_int': (
        ['relations spec does not appear to be well-formed'],
        {
            'services': {
                'django': {'charm': 'cs:trusty/django-42', 'num_units': 1},
            },
            'relations': 42,
        },
    ),
    'test_invalid_relations_section_string': (
        ['relations spec does not appear to be well-formed'],
        {
            'services': {
                'django': {'charm': 'cs:trusty/django-42', 'num_units': 1},
            },
            'relations': 'invalid',
        },
    ),

    # Invalid series.
    'test_invalid_bundle_series_type': (
        ['bundle series must be a string, found []'],
        {
            'series': [],
            'services': {
                'django': {'charm': 'cs:trusty/django-42', 'num_units': 1},
            },
        },
    ),
    'test_invalid_bundle_series_format': (
        ['bundle has invalid series not@valid'],
        {
            'series': 'not@valid',
            'services': {
                'django': {'charm': 'cs:trusty/django-42', 'num_units': 1},
            },
        },
    ),
    'test_invalid_bundle_series_bundle': (
        ['bundle series must specify a charm series'],
        {
            'series': 'bundle',
            'services': {
                'django': {'charm': 'cs:trusty/django-42', 'num_units': 1},
            },
        },
    ),

    # Invalid services.
    'test_invalid_service_name': (
        ['service name 42 must be a string'],
        {
            'services': {
                'django': {'charm': 'cs:trusty/django-42', 'num_units': 1},
                42: {'charm': 'cs:trusty/bad-charm', 'num_units': 1},
            },
        },
    ),
    'test_invalid_service_too_many_units': (
        ['too many units placed for service django'],
        {
            'services': {
                'django': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 2,
                    'to': ['1', 'lxc:1', 'new']
                },
            },
            'machines': {'1': {}},
        },
    ),
    'test_invalid_service_machine_not_referred_to': (
        ['machine 1 not referred to by a placement directive',
         'machine 2 not referred to by a placement directive'],
        {
            'services': {
                'django': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 2,
                    'to': 'new',
                },
            },
            'machines': {'1': {}, '2': {}},
        },
    ),
    'test_invalid_service_charm_url': (
        ['no charm specified for service django',
         'empty charm specified for service haproxy',
         'invalid charm specified for service mysql: 42',
         'invalid charm specified for service rails: '
         'URL has invalid schema: bad'],
        {
            'services': {
                'django': {'num_units': 1},
                'haproxy': {'charm': '', 'num_units': 1},
                'mysql': {'charm': 42, 'num_units': 1},
                'rails': {'charm': 'bad:wolf', 'num_units': 1},
            },
        },
    ),
    'test_invalid_service_charm_reference': (
        ['local charms not allowed for service mysql: local:mysql',
         'bundle cannot be used as charm for service rails: cs:bundle/rails'],
        {
            'services': {
                'mysql': {'charm': 'local:mysql', 'num_units': 1},
                'rails': {'charm': 'bundle/rails', 'num_units': 1},
            },
        },
    ),
    'test_invalid_service_num_units': (
        ['num_units for service django must be a digit',
         'num_units for service haproxy must be a digit',
         'num_units -47 for service mysql must be a positive digit'],
        {
            'services': {
                'django': {'charm': 'django', 'num_units': 'bad-wolf'},
                'haproxy': {'charm': 'haproxy', 'num_units': {}},
                'mysql': {'charm': 'mysql', 'num_units': -47},
            },
        },
    ),
    'test_invalid_service_constraints': (
        ['service django has invalid constraints 47',
         'service memcached has invalid constraints {}',
         'service haproxy has invalid constraints bad wolf',
         'service rails has invalid constraints foo=bar'],
        {
            'services': {
                'django': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 2,
                    'constraints': 47,
                },
                'memcached': {'charm': 'memcached', 'constraints': {}},
                'haproxy': {'charm': 'haproxy', 'constraints': 'bad wolf'},
                'rails': {'charm': 'rails', 'constraints': 'foo=bar'},
            },
        },
    ),
    'test_invalid_service_storage_constraints': (
        ['service django has invalid storage constraints 47',
         'service memcached has invalid storage constraints []',
         'service haproxy has invalid storage constraints bad wolf',
         'service rails has invalid storage constraints foo=bar'],
        {
            'services': {
                'django': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 2,
                    'storage': 47,
                },
                'memcached': {'charm': 'memcached', 'storage': []},
                'haproxy': {'charm': 'haproxy', 'storage': 'bad wolf'},
                'rails': {'charm': 'rails', 'storage': 'foo=bar'},
            },
        },
    ),
    'test_invalid_service_options': (
        ['service django has malformed options',
         'service haproxy has malformed options',
         'service rails has malformed options'],
        {
            'services': {
                'django': {'charm': 'cs:trusty/django-42', 'options': 47},
                'rails': {'charm': 'trusty/rails', 'options': 'bad wolf'},
                'haproxy': {'charm': 'cs:trusty/haproxy', 'options': []},
            },
        },
    ),
    'test_invalid_service_annotations': (
        ['service django has invalid annotations 47',
         'service rails has invalid annotations bad wolf',
         'service haproxy has invalid annotations: keys must be strings'],
        {
            'services': {
                'django': {
                    'charm': 'cs:trusty/django-42',
                    'annotations': 47,
                },
                'rails': {
                    'charm': 'trusty/rails',
                    'annotations': 'bad wolf',
                },
                'haproxy': {
                    'charm': 'cs:trusty/haproxy',
                    'annotations': {'key1': 'value1', None: 42},
                },
            },
        },
    ),
    'test_invalid_service_expose_flag': (
        ['invalid expose value for service django'],
        {
            'series': 'wily',
            'services': {
                'django': {'charm': 'cs:trusty/django-42', 'expose': 'bad'},
            },
        },
    ),

    # Invalid unit placement.
    'test_invalid_machine_placement_v3_bundle': (
        ['too many units placed for service django',
         'invalid container bad for placement bad:wolf',
         'legacy bundles may not place units on machines other than 0',
         'invalid placement 47: placement must be a string'],
        {
            'services': {
                'django': {'charm': 'django', 'to': 'bad:wolf'},
                'rails': {'charm': 'rails', 'num_units': 1, 'to': '1'},
                'haproxy': {'charm': 'haproxy', 'num_units': 1, 'to': 47},
            },
        },
    ),
    'test_invalid_machine_placement_v4_bundle': (
        ['invalid container bad for placement bad:wolf',
         'placement 3 refers to a non-existent machine 3',
         'too many units placed for service haproxy'],
        {
            'services': {
                'django': {
                    'charm': 'django',
                    'num_units': 2,
                    'to': ['1', 'bad:wolf'],
                },
                'rails': {'charm': 'rails', 'num_units': 1, 'to': '3'},
                'haproxy': {
                    'charm': 'haproxy',
                    'num_units': 2,
                    'to': ['1', 'lxc:2', '2'],
                },
            },
            'machines': {1: {}, '2': {}}
        },
    ),
    'test_invalid_service_placement_v3_bundle': (
        ['placement no-such refers to non-existent service no-such',
         'placement no-such=0 refers to non-existent service no-such',
         'unit in placement rails=no-such must be digit',
         'placement haproxy=2 specifies a unit greater than the units in '
         'service haproxy'],
        {
            'services': {
                'django': {
                    'charm': 'utopic/django',
                    'num_units': 1,
                    'to': 'no-such',
                },
                'rails': {'charm': 'rails', 'num_units': 1, 'to': 'no-such=0'},
                'haproxy': {
                    'charm': 'haproxy',
                    'num_units': 1,
                    'to': 'rails=no-such',
                },
                'memcached': {
                    'charm': 'cs:memcached-42',
                    'num_units': 2,
                    'to': 'haproxy=2',
                }
            },
        },
    ),
    'test_invalid_service_placement_v4_bundle': (
        ['charm cs:utopic/django cannot be deployed to machine with different '
         'series trusty',
         'placement no-such refers to non-existent service no-such',
         'placement no-such/0 refers to non-existent service no-such',
         'unit in placement rails/invalid must be digit',
         'placement haproxy/2 specifies a unit greater than the units in '
         'service haproxy'],
        {
            'services': {
                'django': {
                    'charm': 'utopic/django',
                    'num_units': 3,
                    'to': ['no-such', '0', 'lxc:1'],
                },
                'rails': {'charm': 'rails', 'num_units': 1, 'to': 'no-such/0'},
                'haproxy': {
                    'charm': 'haproxy',
                    'num_units': 1,
                    'to': 'rails/invalid',
                },
                'memcached': {
                    'charm': 'cs:memcached-42',
                    'num_units': 2,
                    'to': 'haproxy/2',
                }
            },
            'machines': {
                '0': {
                    'series': 'trusty',
                    'constraints': 'mem=8000',
                    'annotations': {
                        'foo': 'bar',
                    },
                },
                '1': {},
            },
        },
    ),
    'test_invalid_service_placement_num_units': (
        ['machine 0 not referred to by a placement directive',
         'placement 42 refers to a non-existent machine 42',
         'num_units for service rails must be a digit',
         'invalid container no-such for placement no-such:1'],
        {
            'services': {
                'django': {
                    'charm': 'utopic/django',
                    'num_units': 3,
                    'to': ['42', 'lxc:1'],
                },
                'rails': {'charm': 'rails', 'num_units': 'invalid'},
                'haproxy': {
                    'charm': 'haproxy',
                    'num_units': 1,
                    'to': 'rails/0',
                },
                'memcached': {
                    'charm': 'cs:memcached-42',
                    'num_units': 2,
                    'to': 'no-such:1',
                }
            },
            'machines': {
                '0': {
                    'series': 'trusty',
                    'constraints': 'mem=8000',
                    'annotations': {
                        'foo': 'bar',
                    },
                },
                '1': {},
            },
        },
    ),

    # Invalid machines.
    'test_invalid_machines_number': (
        ['machine -1 has an invalid id, must be positive digit',
         'machine -1 not referred to by a placement directive',
         'machine -47 has an invalid id, must be positive digit',
         'machine -47 not referred to by a placement directive'],
        {
            'services': {
                'django': {'charm': 'utopic/django', 'num_units': 3},
            },
            'machines': {
                -1: {
                    'series': 'trusty',
                    'constraints': 'mem=8000',
                    'annotations': {
                        'foo': 'bar',
                    },
                },
                '-47': {},
            },
        },
    ),
    'test_invalid_machines_type': (
        ['machine 1 does not appear to be well-formed'],
        {
            'services': {
                'django': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 1,
                    'to': ['1'],
                },
            },
            'machines': {1: 42},
        },
    ),
    'test_invalid_machines_constraints': (
        ['machine 0 has invalid constraints 47',
         'machine 1 has invalid constraints invalid',
         'machine 2 has invalid constraints no-such=exterminate'],
        {
            'services': {
                'rails': {
                    'charm': 'rails',
                    'num_units': 3,
                    'to': ['0', '1', '2'],
                },
            },
            'machines': {
                '0': {'constraints': 47},
                1: {'series': 'trusty', 'constraints': 'invalid'},
                '2': {'constraints': 'no-such=exterminate'},
            },
        },
    ),
    'test_invalid_machines_series': (
        ['machine 0 series must be a string, found 42',
         'machine 1 has invalid series no:such',
         'machine 2 series must specify a charm series'],
        {
            'services': {
                'rails': {
                    'charm': 'precise/rails',
                    'num_units': 3,
                    'to': ['0', '1', 'lxc:2'],
                },
            },
            'machines': {
                '0': {'series': 42, 'constraints': 'arch=i386'},
                1: {'series': 'no:such', 'annotations': {'key1': 'val1'}},
                '2': {'series': 'bundle', 'annotations': {}},
            },
        },
    ),
    'test_invalid_machines_annotations': (
        ['machine 0 has invalid annotations 42',
         'machine 1 has invalid annotations invalid',
         'machine 2 has invalid annotations: keys must be strings'],
        {
            'services': {
                'rails': {
                    'charm': 'precise/rails',
                    'num_units': 3,
                    'to': ['0', '1', 'lxc:2'],
                },
            },
            'machines': {
                '0': {'annotations': 42},
                1: {'annotations': 'invalid'},
                '2': {'annotations': {'key1': 'value', 42: 'value'}},
            },
        },
    ),
    'test_invalid_machines_multiple_errors': (
        ['machine 0 has invalid annotations exterminate',
         'machine 0 series must specify a charm series',
         'machine 1 has invalid annotations 47',
         'machine 1 series must be a string, found 42',
         'machine 2 has invalid constraints we=are=the=borg'],
        {
            'services': {
                'rails': {
                    'charm': 'precise/rails',
                    'num_units': 3,
                    'to': ['0', '1', 'lxc:2'],
                },
            },
            'machines': {
                '0': {'series': 'bundle', 'annotations': 'exterminate'},
                1: {'series': 42, 'constraints': '', 'annotations': 47},
                '2': {'constraints': 'we=are=the=borg'},
            },
        },
    ),

    # Invalid relations.
    'test_invalid_relations': (
        ['relation 42 is malformed',
         'relation 47 -> django:db has malformed endpoint 47',
         'relation bad wolf is malformed',
         'relation haproxy:web -> {} has malformed endpoint {}',
         'relation mysql:db -> rails:db endpoint rails:db refers to a '
         'non-existent service rails',
         'relation no-such -> django endpoint no-such refers to a '
         'non-existent service no-such'],
        {
            'services': {
                'django': {'charm': 'cs:trusty/django-42', 'num_units': 1},
                'mysql': {'charm': 'trusty/mysql', 'num_units': 1},
                'haproxy': {'charm': 'cs:trusty/haproxy', 'num_units': 1},
            },
            'relations': [
                42,
                [47, 'django:db'],
                ['mysql:db', 'django:db'],
                ['mysql:db', 'rails:db'],
                ['haproxy:web', {}],
                ['haproxy', 'django'],
                ['no-such', 'django'],
                'bad wolf',
            ],
        },
    ),
}


def test_validate():
    """Test bundle validation.

    Single tests are generated using the _validation_tests dict.
    """
    for about, params in _validation_tests.items():
        expected_errors, bundle = params
        yield _make_bundle_validation_check(about), expected_errors, bundle


def _make_bundle_validation_check(about):
    """Generate and return an error test callable."""

    def inner(expected_errors, bundle):
        expected_errors = sorted(expected_errors)
        errors = sorted(validation.validate(bundle))
        msg = (
            'error mismatch\nbundle:\n{}\nerrors:\nexpected {}\nobtained {}'
            ''.format(pprint.pformat(bundle), expected_errors, errors))
        assert expected_errors == errors, msg
    inner.description = about

    return inner

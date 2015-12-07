# Copyright 2015 Canonical Ltd.
# Licensed under the AGPLv3, see LICENCE file for details.

from __future__ import unicode_literals

import unittest

from jujubundlelib import changeset


class TestChangeSet(unittest.TestCase):

    def setUp(self):
        self.cs = changeset.ChangeSet({
            'services': {},
            'machines': {},
            'relations': {},
            'series': 'trusty',
        })

    def test_send_receive(self):
        self.cs.send('foo')
        self.cs.send('bar')
        self.assertEqual(['foo', 'bar'], self.cs.recv())
        self.assertEqual([], self.cs.recv())

    def test_is_legacy_bundle(self):
        self.assertFalse(self.cs.is_legacy_bundle())
        cs = changeset.ChangeSet({'services': {}})
        self.assertTrue(cs.is_legacy_bundle())


class TestParse(unittest.TestCase):

    def handler1(self, changeset):
        for i in range(3):
            changeset.send((1, i))
        return self.handler2

    def handler2(self, changeset):
        for i in range(3):
            changeset.send((2, i))
        return None

    def test_parse(self):
        bundle = {
            'services': {},
            'machines': {},
            'relations': {},
            'series': 'trusty',
        }
        changes = list(changeset.parse(bundle, handler=self.handler1))
        self.assertEqual(
            [
                (1, 0),
                (1, 1),
                (1, 2),
                (2, 0),
                (2, 1),
                (2, 2),
            ],
            changes,
        )

    def test_parse_nothing(self):
        bundle = {'services': {}}
        self.assertEqual([], list(changeset.parse(bundle)))


class TestHandleServices(unittest.TestCase):

    def test_handler(self):
        cs = changeset.ChangeSet({
            # Use an ordered dict so that changes' ids can be predicted
            # deterministically.
            'services': {
                'django': {
                    'charm': 'cs:trusty/django-42',
                },
                'mysql-master': {
                    'charm': 'cs:utopic/mysql-47',
                    'expose': False,
                    'constraints': 'cpu-cores=4 mem=42G',
                },
                'mysql-slave': {
                    'charm': 'cs:utopic/mysql-47',
                    'options': {
                        'key1': 'value1',
                        'key2': 'value2',
                    },
                    'storage': {
                        'data': 'ebs,10G',
                        'cache': 'ebs-ssd',
                    },
                },
                'haproxy': {
                    'charm': 'cs:trusty/haproxy-5',
                    'expose': True,
                    'annotations': {
                        'gui-x': 100,
                        'gui-y': 100,
                    },
                },
            }
        })
        handler = changeset.handle_services(cs)
        self.assertEqual(changeset.handle_machines, handler)
        self.assertEqual(
            [
                {
                    'id': 'addCharm-0',
                    'method': 'addCharm',
                    'args': ['cs:trusty/django-42'],
                    'requires': [],
                },
                {
                    'id': 'deploy-1',
                    'method': 'deploy',
                    'args': ['$addCharm-0', 'django', {}, '', {}],
                    'requires': ['addCharm-0'],
                },
                {
                    'id': 'addCharm-2',
                    'method': 'addCharm',
                    'args': ['cs:trusty/haproxy-5'],
                    'requires': [],
                },
                {
                    'id': 'deploy-3',
                    'method': 'deploy',
                    'args': ['$addCharm-2', 'haproxy', {}, '', {}],
                    'requires': ['addCharm-2'],
                },
                {
                    'id': 'expose-4',
                    'method': 'expose',
                    'args': ['$deploy-3'],
                    'requires': ['deploy-3'],
                },
                {
                    'id': 'setAnnotations-5',
                    'method': 'setAnnotations',
                    'args': [
                        '$deploy-3',
                        'service',
                        {'gui-x': 100, 'gui-y': 100},
                    ],
                    'requires': ['deploy-3'],
                },
                {
                    'id': 'addCharm-6',
                    'method': 'addCharm',
                    'args': ['cs:utopic/mysql-47'],
                    'requires': [],
                },
                {
                    'id': 'deploy-7',
                    'method': 'deploy',
                    'args': [
                        '$addCharm-6',
                        'mysql-master',
                        {},
                        'cpu-cores=4 mem=42G',
                        {},
                    ],
                    'requires': ['addCharm-6'],
                },
                {
                    'id': 'deploy-8',
                    'method': 'deploy',
                    'args': [
                        '$addCharm-6',
                        'mysql-slave',
                        {'key1': 'value1', 'key2': 'value2'},
                        '',
                        {'data': 'ebs,10G', 'cache': 'ebs-ssd'},
                    ],
                    'requires': ['addCharm-6'],
                },
            ],
            cs.recv())

    def test_no_services(self):
        cs = changeset.ChangeSet({'services': {}})
        changeset.handle_services(cs)
        self.assertEqual([], cs.recv())


class TestHandleMachines(unittest.TestCase):

    def test_handler(self):
        cs = changeset.ChangeSet({
            # Use an ordered dict so that changes' ids can be predicted
            # deterministically.
            'machines': {
                '1': {'series': 'vivid'},
                '2': {},
                '42': {'constraints': {'cpu-cores': 4}},
                '23': {'annotations': {'foo': 'bar'}},
            }
        })
        handler = changeset.handle_machines(cs)
        self.assertEqual(changeset.handle_relations, handler)
        self.assertEqual(
            [
                {
                    'id': 'addMachines-0',
                    'method': 'addMachines',
                    'args': [{'constraints': '', 'series': 'vivid'}],
                    'requires': [],
                },
                {
                    'id': 'addMachines-1',
                    'method': 'addMachines',
                    'args': [{'constraints': '', 'series': ''}],
                    'requires': [],
                },
                {
                    'id': 'addMachines-2',
                    'method': 'addMachines',
                    'args': [{'constraints': '', 'series': ''}],
                    'requires': [],
                },
                {
                    'id': 'setAnnotations-3',
                    'method': 'setAnnotations',
                    'args': [
                        '$addMachines-2',
                        'machine',
                        {'foo': 'bar'},
                    ],
                    'requires': ['addMachines-2'],
                },
                {
                    'id': 'addMachines-4',
                    'method': 'addMachines',
                    'args': [{'constraints': {'cpu-cores': 4}, 'series': ''}],
                    'requires': [],
                },
            ],
            cs.recv())

    def test_no_machines(self):
        cs = changeset.ChangeSet({'services': {}})
        changeset.handle_machines(cs)
        self.assertEqual([], cs.recv())

    def test_none_machine(self):
        cs = changeset.ChangeSet({'machines': {42: None}})
        changeset.handle_machines(cs)
        self.assertEqual([{
            'id': 'addMachines-0',
            'method': 'addMachines',
            'args': [{'constraints': '', 'series': ''}],
            'requires': [],
        }], cs.recv())


class TestHandleRelations(unittest.TestCase):

    def test_handler(self):
        cs = changeset.ChangeSet({
            'services': {
                'django': {
                    'charm': 'cs:trusty/django-42',
                },
                'mysql': {
                    'charm': 'cs:utopic/mysql-47',
                },
            },
            'relations': [
                ['mysql:foo', 'django:bar'],
            ],
        })
        cs.services_added = {
            'django': 'deploy-1',
            'mysql': 'deploy-3',
        }
        handler = changeset.handle_relations(cs)
        self.assertEqual(changeset.handle_units, handler)
        self.assertEqual(
            [
                {
                    'id': 'addRelation-0',
                    'method': 'addRelation',
                    'args': ['$deploy-3:foo', '$deploy-1:bar'],
                    'requires': [
                        'deploy-3',
                        'deploy-1'
                    ],
                }
            ], cs.recv()
        )

    def test_no_relations(self):
        cs = changeset.ChangeSet({'relations': []})
        changeset.handle_relations(cs)
        self.assertEqual([], cs.recv())


class TestHandleUnits(unittest.TestCase):

    def test_handler(self):
        cs = changeset.ChangeSet({
            'services': {
                'django': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 1,
                    'to': '42',
                },
                'mysql': {
                    'charm': 'cs:utopic/mysql-47',
                    'num_units': 0,
                },
                'haproxy': {
                    'charm': 'cs:precise/haproxy-0',
                    'num_units': 2,
                },
                'rails': {
                    'charm': 'cs:precise/rails-1',
                    'num_units': 1,
                    'to': ['0'],
                },
            },
            'machines': {0: {}, 42: {}},
        })
        cs.services_added = {
            'django': 'deploy-1',
            'mysql': 'deploy-2',
            'haproxy': 'deploy-3',
            'rails': 'deploy-4',
        }
        cs.machines_added = {
            '0': 'addMachines-0',
            '42': 'addMachines-42',
        }
        handler = changeset.handle_units(cs)
        self.assertIsNone(handler)
        self.assertEqual(
            [
                {
                    'id': 'addUnit-0',
                    'method': 'addUnit',
                    'args': ['$deploy-1', '$addMachines-42'],
                    'requires': ['deploy-1', 'addMachines-42'],
                },
                {
                    'id': 'addUnit-1',
                    'method': 'addUnit',
                    'args': ['$deploy-3', None],
                    'requires': ['deploy-3'],
                },
                {
                    'id': 'addUnit-2',
                    'method': 'addUnit',
                    'args': ['$deploy-3', None],
                    'requires': ['deploy-3'],
                },
                {
                    'id': 'addUnit-3',
                    'method': 'addUnit',
                    'args': ['$deploy-4', '$addMachines-0'],
                    'requires': ['deploy-4', 'addMachines-0'],
                },
            ],
            cs.recv())

    def test_no_units(self):
        cs = changeset.ChangeSet({'services': {}})
        changeset.handle_units(cs)
        self.assertEqual([], cs.recv())

    def test_subordinate_service(self):
        cs = changeset.ChangeSet({'services': {'logger': {'charm': 'logger'}}})
        changeset.handle_units(cs)
        self.assertEqual([], cs.recv())

    def test_unit_in_new_machine(self):
        cs = changeset.ChangeSet({
            'services': {
                'django-new': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 1,
                    'to': 'new',
                },
            },
            'machines': {},
        })
        cs.services_added = {
            'django-new': 'deploy-1',
        }
        handler = changeset.handle_units(cs)
        self.assertIsNone(handler)
        self.assertEqual(
            [
                {
                    'id': 'addMachines-1',
                    'method': 'addMachines',
                    'args': [{}],
                    'requires': [],
                },
                {
                    'id': 'addUnit-0',
                    'method': 'addUnit',
                    'args': ['$deploy-1', '$addMachines-1'],
                    'requires': ['deploy-1', 'addMachines-1'],
                },
            ],
            cs.recv())

    def test_placement_unit_in_service(self):
        cs = changeset.ChangeSet({
            'services': {
                'wordpress': {
                    'charm': 'cs:utopic/wordpress-0',
                    'num_units': 3,
                },
                'django': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 2,
                    'to': ['wordpress'],
                },
            },
            'machines': {},
        })
        cs.services_added = {
            'django': 'deploy-1',
            'wordpress': 'deploy-42',
        }
        handler = changeset.handle_units(cs)
        self.assertIsNone(handler)
        self.assertEqual(
            [
                {
                    'id': 'addUnit-0',
                    'method': 'addUnit',
                    'args': ['$deploy-1', '$addUnit-2'],
                    'requires': ['deploy-1', 'addUnit-2'],
                },
                {
                    'id': 'addUnit-1',
                    'method': 'addUnit',
                    'args': ['$deploy-1', '$addUnit-3'],
                    'requires': ['deploy-1', 'addUnit-3'],
                },
                {
                    'id': 'addUnit-2',
                    'method': 'addUnit',
                    'args': ['$deploy-42', None],
                    'requires': ['deploy-42'],
                },
                {

                    'id': 'addUnit-3',
                    'method': 'addUnit',
                    'args': ['$deploy-42', None],
                    'requires': ['deploy-42'],
                },
                {
                    'id': 'addUnit-4',
                    'method': 'addUnit',
                    'args': ['$deploy-42', None],
                    'requires': ['deploy-42'],
                },
            ],
            cs.recv())

    def test_unit_colocation_to_unit(self):
        cs = changeset.ChangeSet({
            'services': {
                'django-new': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 1,
                },
                'django-unit': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 1,
                    'to': 'django-new/0',
                },
            },
            'machines': {},
        })
        cs.services_added = {
            'django-new': 'deploy-1',
            'django-unit': 'deploy-2',
        }
        handler = changeset.handle_units(cs)
        self.assertIsNone(handler)
        self.assertEqual(
            [
                {
                    'id': 'addUnit-0',
                    'method': 'addUnit',
                    'args': ['$deploy-1', None],
                    'requires': ['deploy-1'],
                },
                {
                    'id': 'addUnit-1',
                    'method': 'addUnit',
                    'args': ['$deploy-2', '$addUnit-0'],
                    'requires': ['deploy-2', 'addUnit-0'],
                },
            ],
            cs.recv())

    def test_unit_in_preexisting_machine(self):
        cs = changeset.ChangeSet({
            'services': {
                'django-machine': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 1,
                    'to': '42',
                },
            },
            'machines': {42: {}},
        })
        cs.services_added = {
            'django-machine': 'deploy-3',
        }
        cs.machines_added = {
            '42': 'addMachines-42',
        }
        handler = changeset.handle_units(cs)
        self.assertIsNone(handler)
        self.assertEqual(
            [
                {
                    'id': 'addUnit-0',
                    'method': 'addUnit',
                    'args': ['$deploy-3', '$addMachines-42'],
                    'requires': ['deploy-3', 'addMachines-42'],
                },
            ],
            cs.recv())

    def test_unit_in_new_machine_container(self):
        cs = changeset.ChangeSet({
            'services': {
                'django-new-lxc': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 1,
                    'to': 'lxc:new',
                },
            },
            'machines': {},
        })
        cs.services_added = {
            'django-new-lxc': 'deploy-4',
        }
        handler = changeset.handle_units(cs)
        self.assertIsNone(handler)
        self.assertEqual(
            [
                {
                    'id': 'addMachines-1',
                    'method': 'addMachines',
                    'args': [{'containerType': 'lxc'}],
                    'requires': [],
                },
                {
                    'id': 'addUnit-0',
                    'method': 'addUnit',
                    'args': ['$deploy-4', '$addMachines-1'],
                    'requires': ['deploy-4', 'addMachines-1'],
                },
            ],
            cs.recv())

    def test_unit_colocation_to_container_in_unit(self):
        cs = changeset.ChangeSet({
            'services': {
                'django-new': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 1,
                },
                'django-unit-lxc': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 1,
                    'to': 'lxc:django-new/0',
                },
            },
            'machines': {},
        })
        cs.services_added = {
            'django-new': 'deploy-1',
            'django-unit-lxc': 'deploy-5',
        }
        handler = changeset.handle_units(cs)
        self.assertIsNone(handler)
        self.maxDiff = None
        self.assertEqual(
            [
                {
                    'id': 'addUnit-0',
                    'method': 'addUnit',
                    'args': ['$deploy-1', None],
                    'requires': ['deploy-1'],
                },
                {
                    'id': 'addMachines-2',
                    'method': 'addMachines',
                    'args': [{
                        'containerType': 'lxc',
                        'parentId': '$addUnit-0',
                    }],
                    'requires': ['addUnit-0'],
                },
                {
                    'id': 'addUnit-1',
                    'method': 'addUnit',
                    'args': ['$deploy-5', '$addMachines-2'],
                    'requires': ['deploy-5', 'addMachines-2'],
                },
            ],
            cs.recv())

    def test_placement_unit_in_container_in_service(self):
        cs = changeset.ChangeSet({
            'services': {
                'wordpress': {
                    'charm': 'cs:utopic/wordpress-0',
                    'num_units': 1,
                },
                'rails': {
                    'charm': 'cs:utopic/rails-0',
                    'num_units': 2,
                },
                'django': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 3,
                    'to': ['lxc:wordpress', 'kvm:rails'],
                },
            },
            'machines': {},
        })
        cs.services_added = {
            'django': 'deploy-1',
            'wordpress': 'deploy-42',
            'rails': 'deploy-47',
        }
        handler = changeset.handle_units(cs)
        self.assertIsNone(handler)
        self.assertEqual(
            [
                {
                    'id': 'addMachines-6',
                    'method': 'addMachines',
                    'args': [{
                        'containerType': 'lxc',
                        'parentId': '$addUnit-5',
                    }],
                    'requires': ['addUnit-5'],
                },
                {
                    'id': 'addUnit-0',
                    'method': 'addUnit',
                    'args': ['$deploy-1', '$addMachines-6'],
                    'requires': ['deploy-1', 'addMachines-6'],
                },
                {
                    'id': 'addMachines-7',
                    'method': 'addMachines',
                    'args': [{
                        'containerType': 'kvm',
                        'parentId': '$addUnit-3',
                    }],
                    'requires': ['addUnit-3'],
                },
                {
                    'id': 'addUnit-1',
                    'method': 'addUnit',
                    'args': ['$deploy-1', '$addMachines-7'],
                    'requires': ['deploy-1', 'addMachines-7'],
                },
                {
                    'id': 'addMachines-8',
                    'method': 'addMachines',
                    'args': [{
                        'containerType': 'kvm',
                        'parentId': '$addUnit-4',
                    }],
                    'requires': ['addUnit-4'],
                },
                {
                    'id': 'addUnit-2',
                    'method': 'addUnit',
                    'args': ['$deploy-1', '$addMachines-8'],
                    'requires': ['deploy-1', 'addMachines-8'],
                },
                {
                    'id': 'addUnit-3',
                    'method': 'addUnit',
                    'args': ['$deploy-47', None],
                    'requires': ['deploy-47'],
                },
                {
                    'id': 'addUnit-4',
                    'method': 'addUnit',
                    'args': ['$deploy-47', None],
                    'requires': ['deploy-47'],
                },
                {
                    'id': 'addUnit-5',
                    'method': 'addUnit',
                    'args': ['$deploy-42', None],
                    'requires': ['deploy-42'],
                },
            ],
            cs.recv())

    def test_unit_in_preexisting_machine_container(self):
        cs = changeset.ChangeSet({
            'services': {
                'django-machine-lxc': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 1,
                    'to': 'lxc:0',
                },
            },
            'machines': {0: {}},
        })
        cs.services_added = {
            'django-machine-lxc': 'deploy-6',
        }
        cs.machines_added = {
            '0': 'addMachines-47',
        }
        handler = changeset.handle_units(cs)
        self.assertIsNone(handler)
        self.assertEqual(
            [
                {
                    'id': 'addMachines-1',
                    'method': 'addMachines',
                    'args': [{
                        'containerType': 'lxc',
                        'parentId': '$addMachines-47',
                    }],
                    'requires': ['addMachines-47'],
                },
                {
                    'id': 'addUnit-0',
                    'method': 'addUnit',
                    'args': ['$deploy-6', '$addMachines-1'],
                    'requires': ['deploy-6', 'addMachines-1'],
                },
            ],
            cs.recv())

    def test_v3_placement_unit_in_bootstrap_node(self):
        cs = changeset.ChangeSet({
            'services': {
                'django': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 1,
                    'to': '0',
                },
            },
        })
        cs.services_added = {
            'django': 'deploy-1',
        }
        handler = changeset.handle_units(cs)
        self.assertIsNone(handler)
        self.assertEqual(
            [
                {
                    'id': 'addUnit-0',
                    'method': 'addUnit',
                    'args': ['$deploy-1', '0'],
                    'requires': ['deploy-1'],
                },
            ],
            cs.recv())

    def test_v3_placement_unit_in_service(self):
        cs = changeset.ChangeSet({
            'services': {
                'wordpress': {
                    'charm': 'cs:utopic/wordpress-0',
                    'num_units': 3,
                },
                'django': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 2,
                    'to': ['wordpress', 'wordpress'],
                },
            },
        })
        cs.services_added = {
            'django': 'deploy-1',
            'wordpress': 'deploy-42',
        }
        handler = changeset.handle_units(cs)
        self.assertIsNone(handler)
        self.assertEqual(
            [
                {
                    'id': 'addUnit-0',
                    'method': 'addUnit',
                    'args': ['$deploy-1', '$addUnit-2'],
                    'requires': ['deploy-1', 'addUnit-2'],
                },
                {
                    'id': 'addUnit-1',
                    'method': 'addUnit',
                    'args': ['$deploy-1', '$addUnit-3'],
                    'requires': ['deploy-1', 'addUnit-3'],
                },
                {
                    'id': 'addUnit-2',
                    'method': 'addUnit',
                    'args': ['$deploy-42', None],
                    'requires': ['deploy-42'],
                },
                {

                    'id': 'addUnit-3',
                    'method': 'addUnit',
                    'args': ['$deploy-42', None],
                    'requires': ['deploy-42'],
                },
                {
                    'id': 'addUnit-4',
                    'method': 'addUnit',
                    'args': ['$deploy-42', None],
                    'requires': ['deploy-42'],
                },
            ],
            cs.recv())

    def test_v3_placement_unit_in_unit(self):
        cs = changeset.ChangeSet({
            'services': {
                'wordpress': {
                    'charm': 'cs:utopic/wordpress-0',
                    'num_units': 1,
                },
                'django': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 1,
                    'to': 'wordpress=0',
                },
            },
        })
        cs.services_added = {
            'django': 'deploy-1',
            'wordpress': 'deploy-42',
        }
        handler = changeset.handle_units(cs)
        self.assertIsNone(handler)
        self.assertEqual(
            [
                {
                    'id': 'addUnit-0',
                    'method': 'addUnit',
                    'args': ['$deploy-1', '$addUnit-1'],
                    'requires': ['deploy-1', 'addUnit-1'],
                },
                {
                    'id': 'addUnit-1',
                    'method': 'addUnit',
                    'args': ['$deploy-42', None],
                    'requires': ['deploy-42'],
                },
            ],
            cs.recv())

    def test_v3_placement_unit_in_lxc_in_service(self):
        cs = changeset.ChangeSet({
            'services': {
                'wordpress': {
                    'charm': 'cs:utopic/wordpress-0',
                    'num_units': 1,
                },
                'django': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 1,
                    'to': 'lxc:wordpress',
                },
            },
        })
        cs.services_added = {
            'django': 'deploy-1',
            'wordpress': 'deploy-42',
        }
        handler = changeset.handle_units(cs)
        self.assertIsNone(handler)
        self.assertEqual(
            [
                {
                    'id': 'addMachines-2',
                    'method': 'addMachines',
                    'args': [{
                        'containerType': 'lxc',
                        'parentId': '$addUnit-1',
                    }],
                    'requires': ['addUnit-1'],
                },
                {
                    'id': 'addUnit-0',
                    'method': 'addUnit',
                    'args': ['$deploy-1', '$addMachines-2'],
                    'requires': ['deploy-1', 'addMachines-2'],
                },
                {
                    'id': 'addUnit-1',
                    'method': 'addUnit',
                    'args': ['$deploy-42', None],
                    'requires': ['deploy-42'],
                },
            ],
            cs.recv())

    def test_v3_placement_unit_in_lxc_in_unit(self):
        cs = changeset.ChangeSet({
            'services': {
                'wordpress': {
                    'charm': 'cs:utopic/wordpress-0',
                    'num_units': 1,
                },
                'django': {
                    'charm': 'cs:trusty/django-42',
                    'num_units': 1,
                    'to': 'lxc:wordpress=0',
                },
            },
        })
        cs.services_added = {
            'django': 'deploy-1',
            'wordpress': 'deploy-42',
        }
        handler = changeset.handle_units(cs)
        self.assertIsNone(handler)
        self.assertEqual(
            [
                {
                    'id': 'addMachines-2',
                    'method': 'addMachines',
                    'args': [{
                        'containerType': 'lxc',
                        'parentId': '$addUnit-1',
                    }],
                    'requires': ['addUnit-1'],
                },
                {
                    'id': 'addUnit-0',
                    'method': 'addUnit',
                    'args': ['$deploy-1', '$addMachines-2'],
                    'requires': ['deploy-1', 'addMachines-2'],
                },
                {
                    'id': 'addUnit-1',
                    'method': 'addUnit',
                    'args': ['$deploy-42', None],
                    'requires': ['deploy-42'],
                },
            ],
            cs.recv())

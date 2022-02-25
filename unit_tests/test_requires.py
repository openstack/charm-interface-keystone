# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import unittest
from unittest import mock

import requires


_hook_args = {}


def mock_hook(*args, **kwargs):

    def inner(f):
        # remember what we were passed.  Note that we can't actually determine
        # the class we're attached to, as the decorator only gets the function.
        _hook_args[f.__name__] = dict(args=args, kwargs=kwargs)
        return f
    return inner


class TestKeystoneRequires(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._patched_hook = mock.patch('charms.reactive.hook', mock_hook)
        cls._patched_hook_started = cls._patched_hook.start()
        # force requires to rerun the mock_hook decorator:
        # try except is Python2/Python3 compatibility as Python3 has moved
        # reload to importlib.
        try:
            reload(requires)
        except NameError:
            import importlib
            importlib.reload(requires)

    @classmethod
    def tearDownClass(cls):
        cls._patched_hook.stop()
        cls._patched_hook_started = None
        cls._patched_hook = None
        # and fix any breakage we did to the module
        try:
            reload(requires)
        except NameError:
            import importlib
            importlib.reload(requires)

    def setUp(self):
        self.kr = requires.KeystoneRequires('some-relation', [])
        self._patches = {}
        self._patches_start = {}

    def tearDown(self):
        self.kr = None
        for k, v in self._patches.items():
            v.stop()
            setattr(self, k, None)
        self._patches = None
        self._patches_start = None

    def patch_kr(self, attr, return_value=None):
        mocked = mock.patch.object(self.kr, attr)
        self._patches[attr] = mocked
        started = mocked.start()
        started.return_value = return_value
        self._patches_start[attr] = started
        setattr(self, attr, started)

    def test_registered_hooks(self):
        # test that the hooks actually registered the relation expressions that
        # are meaningful for this interface: this is to handle regressions.
        # The keys are the function names that the hook attaches to.
        hook_patterns = {
            'joined': ('{requires:keystone}-relation-joined', ),
            'changed': ('{requires:keystone}-relation-changed', ),
            'departed': ('{requires:keystone}-relation-{broken,departed}', ),
        }
        for k, v in _hook_args.items():
            self.assertEqual(hook_patterns[k], v['args'])

    def test_changed(self):
        self.patch_kr('update_state')
        self.kr.changed()
        self.update_state.assert_called_once_with()

    def test_joined(self):
        self.patch_kr('update_state')
        self.patch_kr('set_state')
        self.kr.joined()
        self.set_state.assert_called_once_with('{relation_name}.connected')
        self.update_state.assert_called_once_with()

    def test_departed(self):
        self.patch_kr('update_state')
        self.kr.departed()
        self.update_state.assert_called_once_with()

    def test_base_data_complete(self):
        self.patch_kr('private_address', '1')
        self.patch_kr('service_host', '2')
        self.patch_kr('service_protocol', '3')
        self.patch_kr('service_port', '4')
        self.patch_kr('auth_host', '5')
        self.patch_kr('auth_protocol', '6')
        self.patch_kr('auth_port', '7')
        self.patch_kr('service_tenant', '1')
        self.patch_kr('service_username', '2')
        self.patch_kr('service_password', '3')
        self.patch_kr('service_tenant_id', '4')
        assert self.kr.base_data_complete() is True
        self.service_tenant.return_value = None
        assert self.kr.base_data_complete() is False

    def test_ssl_data_complete(self):
        self.patch_kr('ssl_cert_admin', '1')
        self.patch_kr('ssl_cert_internal', '2')
        self.patch_kr('ssl_cert_public', '3')
        self.patch_kr('ssl_key_admin', '4')
        self.patch_kr('ssl_key_internal', '5')
        self.patch_kr('ssl_key_public', '6')
        self.patch_kr('ca_cert', '7')
        assert self.kr.ssl_data_complete() is True
        self.ca_cert.return_value = None
        assert self.kr.ssl_data_complete() is False
        self.ca_cert.return_value = '7'
        self.ssl_key_public.return_value = '__null__'
        assert self.kr.ssl_data_complete() is False

    def test_ssl_data_complete_legacy(self):
        self.patch_kr('ssl_key', '1')
        self.patch_kr('ssl_cert', '2')
        self.patch_kr('ca_cert', '3')
        assert self.kr.ssl_data_complete_legacy() is True
        self.ca_cert.return_value = None
        assert self.kr.ssl_data_complete_legacy() is False
        self.ca_cert.return_value = '3'
        self.ssl_key.return_value = '__null__'
        assert self.kr.ssl_data_complete_legacy() is False

    def test_update_state(self):
        self.patch_kr('base_data_complete', False)
        self.patch_kr('ssl_data_complete', False)
        self.patch_kr('ssl_data_complete_legacy', False)
        self.patch_kr('set_state')
        self.patch_kr('remove_state')
        # test when not all base data is available.
        self.kr.update_state()
        self.remove_state.assert_any_call('{relation_name}.available')
        self.remove_state.assert_any_call('{relation_name}.available.ssl')
        self.remove_state.assert_any_call(
            '{relation_name}.available.ssl_legacy')
        self.remove_state.assert_any_call('{relation_name}.available.auth')
        self.set_state.assert_not_called()
        self.remove_state.reset_mock()
        # test when just the base data is available.
        self.base_data_complete.return_value = True
        self.kr.update_state()
        self.set_state.assert_any_call('{relation_name}.available')
        self.set_state.assert_any_call('{relation_name}.available.auth')
        self.remove_state.assert_any_call('{relation_name}.available.ssl')
        self.remove_state.assert_any_call(
            '{relation_name}.available.ssl_legacy')
        self.set_state.reset_mock()
        self.remove_state.reset_mock()
        # test ssl_data_complete
        self.ssl_data_complete.return_value = True
        self.kr.update_state()
        self.set_state.assert_any_call('{relation_name}.available')
        self.set_state.assert_any_call('{relation_name}.available.ssl')
        self.remove_state.assert_any_call(
            '{relation_name}.available.ssl_legacy')
        self.set_state.reset_mock()
        self.remove_state.reset_mock()
        # test ssl_data_complete_legacy
        self.ssl_data_complete_legacy.return_value = True
        self.kr.update_state()
        self.set_state.assert_any_call('{relation_name}.available')
        self.set_state.assert_any_call('{relation_name}.available.ssl')
        self.set_state.assert_any_call(
            '{relation_name}.available.ssl_legacy')
        self.set_state.reset_mock()
        self.remove_state.reset_mock()
        self.kr.update_state()
        self.set_state.assert_any_call('{relation_name}.available')
        self.set_state.assert_any_call('{relation_name}.available.ssl')
        self.set_state.assert_any_call(
            '{relation_name}.available.ssl_legacy')
        self.set_state.assert_any_call('{relation_name}.available.auth')
        self.remove_state.assert_not_called()

    def test_register_endpoints(self):
        self.patch_kr('set_local')
        self.patch_kr('set_remote')
        self.kr.register_endpoints('s', 'r', 'p_url', 'i_url', 'a_url')
        result = {
            'service': 's',
            'public_url': 'p_url',
            'internal_url': 'i_url',
            'admin_url': 'a_url',
            'region': 'r',
        }
        self.set_local.assert_called_once_with(**result)
        self.set_remote.assert_called_once_with(**result)

    def test_register_endpoints_requested_roles(self):
        self.patch_kr('set_local')
        self.patch_kr('set_remote')
        self.kr.register_endpoints('s', 'r', 'p_url', 'i_url', 'a_url',
                                   requested_roles=['role1', 'role2'])
        result = {
            'service': 's',
            'public_url': 'p_url',
            'internal_url': 'i_url',
            'admin_url': 'a_url',
            'region': 'r',
            'requested_roles': 'role1,role2',
        }
        self.set_local.assert_called_once_with(**result)
        self.set_remote.assert_called_once_with(**result)

    def test_register_endpoints_add_role_to_admin(self):
        self.patch_kr('set_local')
        self.patch_kr('set_remote')
        self.kr.register_endpoints('s', 'r', 'p_url', 'i_url', 'a_url',
                                   requested_roles=['role1', 'role2'],
                                   add_role_to_admin=['grole1', 'grole2'])
        result = {
            'service': 's',
            'public_url': 'p_url',
            'internal_url': 'i_url',
            'admin_url': 'a_url',
            'region': 'r',
            'requested_roles': 'role1,role2',
            'add_role_to_admin': 'grole1,grole2',
        }
        self.set_local.assert_called_once_with(**result)
        self.set_remote.assert_called_once_with(**result)

    def test_request_keystone_endpoint_information(self):
        self.patch_kr('set_local')
        self.patch_kr('set_remote')
        result = {
            'service': 'None',
            'public_url': 'None',
            'internal_url': 'None',
            'admin_url': 'None',
            'region': 'None',
        }
        self.kr.request_keystone_endpoint_information()
        self.set_local.assert_called_once_with(**result)
        self.set_remote.assert_called_once_with(**result)

    def test_request_notification(self):
        self.patch_kr('set_remote')
        result = {
            'subscribe_ep_change': 'nova neutron'
        }
        self.kr.request_notification(['nova', 'neutron'])
        self.set_remote.assert_called_once_with(**result)

    def test_endpoint_checksums(self):
        self.patch_kr('ep_changed')
        self.kr.ep_changed.return_value = (
            '{"nova": "abxcxv", "neutron": "124252"}'
        )
        result = {
            'nova': 'abxcxv',
            'neutron': '124252',
        }
        self.assertEqual(self.kr.endpoint_checksums(), result)

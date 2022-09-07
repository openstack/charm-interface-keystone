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


from unittest import mock

import requires

import charms_openstack.test_utils as test_utils

_hook_args = {}


class TestKeystoneRequires(test_utils.PatchHelper):

    def setUp(self):
        self.target = requires.KeystoneRequires('some-relation', [])
        self._patches = {}
        self._patches_start = {}

    def tearDown(self):
        self.target = None
        for k, v in self._patches.items():
            v.stop()
            setattr(self, k, None)
        self._patches = None
        self._patches_start = None

    def patch_target(self, attr, return_value=None):
        mocked = mock.patch.object(self.target, attr)
        self._patches[attr] = mocked
        started = mocked.start()
        started.return_value = return_value
        self._patches_start[attr] = started
        setattr(self, attr, started)

    def test_joined(self):
        self.patch_object(requires.reactive, 'set_flag')
        self.target.joined()
        self.set_flag.assert_called_once_with('some-relation.connected')

    def test_departed(self):
        self.patch_object(requires.reactive, 'clear_flag')
        self.patch_target('update_flags')
        self.target.departed()
        self.clear_flag.assert_has_calls([
            mock.call('endpoint.some-relation.departed')
        ])
        self.update_flags.assert_called_once_with()

    def test_base_data_complete(self):
        self.patch_target('service_host', '2')
        self.patch_target('service_protocol', '3')
        self.patch_target('service_port', '4')
        self.patch_target('auth_host', '5')
        self.patch_target('auth_protocol', '6')
        self.patch_target('auth_port', '7')
        self.patch_target('service_tenant', '1')
        self.patch_target('service_username', '2')
        self.patch_target('service_password', '3')
        self.patch_target('service_tenant_id', '4')
        self.patch_target('service_type', 'identity')
        assert self.target.base_data_complete() is True
        self.service_tenant.return_value = None
        assert self.target.base_data_complete() is False

    def test_ssl_data_complete(self):
        self.patch_target('ssl_cert_admin', '1')
        self.patch_target('ssl_cert_internal', '2')
        self.patch_target('ssl_cert_public', '3')
        self.patch_target('ssl_key_admin', '4')
        self.patch_target('ssl_key_internal', '5')
        self.patch_target('ssl_key_public', '6')
        self.patch_target('ca_cert', '7')
        assert self.target.ssl_data_complete() is True
        self.ca_cert.return_value = None
        assert self.target.ssl_data_complete() is False
        self.ca_cert.return_value = '7'
        self.ssl_key_public.return_value = '__null__'
        assert self.target.ssl_data_complete() is False

    def test_ssl_data_complete_legacy(self):
        self.patch_target('ssl_key', '1')
        self.patch_target('ssl_cert', '2')
        self.patch_target('ca_cert', '3')
        assert self.target.ssl_data_complete_legacy() is True
        self.ca_cert.return_value = None
        assert self.target.ssl_data_complete_legacy() is False
        self.ca_cert.return_value = '3'
        self.ssl_key.return_value = '__null__'
        assert self.target.ssl_data_complete_legacy() is False

    def test_changed(self):
        self.patch_target('base_data_complete', False)
        self.patch_target('ssl_data_complete', False)
        self.patch_target('ssl_data_complete_legacy', False)
        self.patch_object(requires.reactive, 'set_flag')
        self.patch_object(requires.reactive, 'clear_flag')
        # test when not all base data is available.
        self.target.changed()
        self.clear_flag.assert_any_call('some-relation.available')
        self.clear_flag.assert_any_call('some-relation.available.ssl')
        self.clear_flag.assert_any_call(
            'some-relation.available.ssl_legacy')
        self.clear_flag.assert_any_call('some-relation.available.auth')
        self.set_flag.assert_not_called()
        self.clear_flag.assert_any_call(
            'endpoint.some-relation.changed')
        self.clear_flag.reset_mock()
        # test when just the base data is available.
        self.base_data_complete.return_value = True
        self.target.changed()
        self.set_flag.assert_any_call('some-relation.available')
        self.set_flag.assert_any_call('some-relation.available.auth')
        self.clear_flag.assert_any_call('some-relation.available.ssl')
        self.clear_flag.assert_any_call(
            'some-relation.available.ssl_legacy')
        self.clear_flag.assert_any_call(
            'endpoint.some-relation.changed')
        self.set_flag.reset_mock()
        self.clear_flag.reset_mock()
        # test ssl_data_complete
        self.ssl_data_complete.return_value = True
        self.target.changed()
        self.set_flag.assert_any_call('some-relation.available')
        self.set_flag.assert_any_call('some-relation.available.auth')
        self.set_flag.assert_any_call('some-relation.available.ssl')
        self.clear_flag.assert_any_call(
            'some-relation.available.ssl_legacy')
        self.clear_flag.assert_any_call(
            'endpoint.some-relation.changed')
        self.set_flag.reset_mock()
        self.clear_flag.reset_mock()
        # test ssl_data_complete_legacy
        self.ssl_data_complete_legacy.return_value = True
        self.target.changed()
        self.set_flag.assert_any_call('some-relation.available')
        self.set_flag.assert_any_call('some-relation.available.auth')
        self.set_flag.assert_any_call('some-relation.available.ssl')
        self.set_flag.assert_any_call(
            'some-relation.available.ssl_legacy')
        self.clear_flag.assert_any_call(
            'endpoint.some-relation.changed')

    def test_register_endpoints(self):
        relation = mock.MagicMock()
        self.patch_target('_relations')
        self._relations.__iter__.return_value = [relation]
        self.target.register_endpoints('s', 'r', 'p_url', 'i_url', 'a_url')
        result = {
            'service': 's',
            'public_url': 'p_url',
            'internal_url': 'i_url',
            'admin_url': 'a_url',
            'region': 'r',
        }
        relation.to_publish_raw.update.assert_called_once_with(result)

    def test_register_endpoints_requested_roles(self):
        relation = mock.MagicMock()
        self.patch_target('_relations')
        self._relations.__iter__.return_value = [relation]
        self.target.register_endpoints(
            's', 'r', 'p_url', 'i_url', 'a_url',
            requested_roles=['role1', 'role2'])
        result = {
            'service': 's',
            'public_url': 'p_url',
            'internal_url': 'i_url',
            'admin_url': 'a_url',
            'region': 'r',
            'requested_roles': 'role1,role2',
        }
        relation.to_publish_raw.update.assert_called_once_with(result)

    def test_register_endpoints_add_role_to_admin(self):
        relation = mock.MagicMock()
        self.patch_target('_relations')
        self._relations.__iter__.return_value = [relation]
        self.target.register_endpoints('s', 'r', 'p_url', 'i_url', 'a_url',
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
        relation.to_publish_raw.update.assert_called_once_with(result)

    def test_request_keystone_endpoint_information(self):
        relation = mock.MagicMock()
        self.patch_target('_relations')
        self._relations.__iter__.return_value = [relation]
        result = {
            'service': 'None',
            'public_url': 'None',
            'internal_url': 'None',
            'admin_url': 'None',
            'region': 'None',
        }
        self.target.request_keystone_endpoint_information()
        relation.to_publish_raw.update.assert_called_once_with(result)

    def test_request_notification(self):
        relation = mock.MagicMock()
        self.patch_target('_relations')
        self._relations.__iter__.return_value = [relation]
        result = {
            'subscribe_ep_change': 'nova neutron'
        }
        self.target.request_notification(['nova', 'neutron'])
        relation.to_publish_raw.update.assert_called_once_with(result)

    def test_endpoint_checksums(self):
        self.patch_target('ep_changed')
        self.target.ep_changed.return_value = (
            '{"nova": "abxcxv", "neutron": "124252"}'
        )
        result = {
            'nova': 'abxcxv',
            'neutron': '124252',
        }
        self.assertEqual(self.target.endpoint_checksums(), result)

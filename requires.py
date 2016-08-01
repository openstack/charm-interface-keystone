#!/usr/bin/python
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

import base64

from charms.reactive import RelationBase
from charms.reactive import hook
from charms.reactive import scopes


class KeystoneRequires(RelationBase):
    scope = scopes.GLOBAL

    # These remote data fields will be automatically mapped to accessors
    # with a basic documentation string provided.

    auto_accessors = ['private-address', 'service_host', 'service_protocol',
                      'service_port', 'service_tenant', 'service_username',
                      'service_password', 'service_tenant_id', 'auth_host',
                      'auth_protocol', 'auth_port', 'admin_token', 'ssl_key',
                      'ca_cert', 'ssl_cert', 'https_keystone',
                      'ssl_cert_admin', 'ssl_cert_internal',
                      'ssl_cert_public', 'ssl_key_admin', 'ssl_key_internal',
                      'ssl_key_public', 'api_version']

    @hook('{requires:keystone}-relation-joined')
    def joined(self):
        self.set_state('{relation_name}.connected')
        self.update_state()

    def update_state(self):
        if self.base_data_complete():
            self.set_state('{relation_name}.available')
            if self.ssl_data_complete():
                self.set_state('{relation_name}.available.ssl')
            else:
                self.remove_state('{relation_name}.available.ssl')
            if self.ssl_data_complete_legacy():
                self.set_state('{relation_name}.available.ssl_legacy')
            else:
                self.remove_state('{relation_name}.available.ssl_legacy')
            if self.auth_data_complete():
                self.set_state('{relation_name}.available.auth')
            else:
                self.remove_state('{relation_name}.available.auth')
        else:
            self.remove_state('{relation_name}.available')
            self.remove_state('{relation_name}.available.ssl')
            self.remove_state('{relation_name}.available.ssl_legacy')
            self.remove_state('{relation_name}.available.auth')

    @hook('{requires:keystone}-relation-changed')
    def changed(self):
        self.update_state()

    @hook('{requires:keystone}-relation-{broken,departed}')
    def departed(self):
        self.update_state()

    def base_data_complete(self):
        data = {
            'private-address': self.private_address(),
            'service_host': self.service_host(),
            'service_protocol': self.service_protocol(),
            'service_port': self.service_port(),
            'auth_host': self.auth_host(),
            'auth_protocol': self.auth_protocol(),
            'auth_port': self.auth_port(),
        }
        if all(data.values()):
            return True
        return False

    def auth_data_complete(self):
        data = {
            'service_tenant': self.service_tenant(),
            'service_username': self.service_username(),
            'service_password': self.service_password(),
            'service_tenant_id': self.service_tenant_id(),
        }
        if all(data.values()):
            return True
        return False

    def ssl_data_complete(self):
        data = {
            'ssl_cert_admin': self.ssl_cert_admin(),
            'ssl_cert_internal': self.ssl_cert_internal(),
            'ssl_cert_public': self.ssl_cert_public(),
            'ssl_key_admin': self.ssl_key_admin(),
            'ssl_key_internal': self.ssl_key_internal(),
            'ssl_key_public': self.ssl_key_public(),
            'ca_cert': self.ca_cert(),
        }
        for value in data.values():
            if not value or value == '__null__':
                return False
        return True

    def ssl_data_complete_legacy(self):
        data = {
            'ssl_key': self.ssl_key(),
            'ssl_cert': self.ssl_cert(),
            'ca_cert': self.ca_cert(),
        }
        for value in data.values():
            if not value or value == '__null__':
                return False
        return True

    def register_endpoints(self, service, region, public_url, internal_url,
                           admin_url):
        """
        Register this service with keystone
        """
        relation_info = {
            'service': service,
            'public_url': public_url,
            'internal_url': internal_url,
            'admin_url': admin_url,
            'region': region,
        }
        self.set_local(**relation_info)
        self.set_remote(**relation_info)

    def request_keystone_endpoint_information(self):
        self.register_endpoints('None', 'None', 'None', 'None', 'None')

    def get_ssl_key(self, cn=None):
        relation_key = 'ssl_key_{}'.format(cn) if cn else 'ssl_key'
        key = self.get_remote(relation_key)
        if key:
            key = base64.b64decode(key).decode('utf-8')
        return key

    def get_ssl_cert(self, cn=None):
        relation_key = 'ssl_cert_{}'.format(cn) if cn else 'ssl_cert'
        cert = self.get_remote(relation_key)
        if cert:
            cert = base64.b64decode(cert).decode('utf-8')
        return cert

    def get_ssl_ca(self, cn=None):
        ca = None
        if self.ca_cert():
            ca = base64.b64decode(self.ca_cert()).decode('utf-8')
        return ca

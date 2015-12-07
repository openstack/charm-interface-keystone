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
                      'ssl_key_public']

    @hook('{requires:keystone}-relation-joined')
    def joined(self):
        self.set_state('{relation_name}.connected')

    def update_state(self):
        if self.base_data_complete():
            self.set_state('{relation_name}.available')
            if self.ssl_data_complete():
                self.set_state('{relation_name}.available.ssl')
            else:
                self.remove_state('{relation_name}.available.ssl')
        else:
            self.remove_state('{relation_name}.available')
            self.remove_state('{relation_name}.available.ssl')

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
            'service_tenant': self.service_tenant(),
            'service_username': self.service_username(),
            'service_password': self.service_password(),
            'service_tenant_id': self.service_tenant_id(),
            'auth_host': self.auth_host(),
            'auth_protocol': self.auth_protocol(),
            'auth_port': self.auth_port(),
            'admin_token': self.admin_token(),
        }
        if all(data.values()):
            return True
        return False

    def ssl_data_complete(self):
        data = {
            'ssl_key': self.ssl_key(),
            'ssl_cert': self.ssl_cert(),
            'ssl_cert_admin': self.ssl_cert_admin(),
            'ssl_cert_internal': self.ssl_cert_internal(),
            'ssl_cert_public': self.ssl_cert_public(),
            'ssl_key_admin': self.ssl_key_admin(),
            'ssl_key_internal': self.ssl_key_internal(),
            'ssl_key_public': self.ssl_key_public(),
            'ca_cert': self.ca_cert(),
            'https_keystone': self.https_keystone(),
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

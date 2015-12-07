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
                      'service_password', 'auth_host', 'auth_protocol',
                      'auth_port', 'admin_tenant_id']

    @hook('{requires:keystone}-relation-joined')
    def joined(self):
        self.set_state('{relation_name}.connected')

    def update_state(self):
        if self.base_data_complete():
            self.set_state('{relation_name}.available')
        else:
            self.remove_state('{relation_name}.available')
        if not self.keystone_hosts():
            self.remove_state('{relation_name}.connected')

    @hook('{requires:keystone}-relation-changed')
    def changed(self):
        self.update_state()

    @hook('{requires:keystone}-relation-{broken,departed}')
    def departed(self):
        self.update_state()

    def base_data_complete(self):
        """
        Get the connection string, if available, or None.
        """
        for field in self.auto_accessors:
            if not self.get(field):
                return False
        return True

    def register_endpoints(self, public_url, internal_url, admin_url):
        """
        Register this service with keystone
        """
        relation_info = {
            'public_url': public_url,
            'internal_url': internal_url,
            'admin_url': admin_url,
        }
        self.set_local(**relation_info)
        self.set_remote(**relation_info)

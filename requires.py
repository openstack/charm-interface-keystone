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
import json

import charms.reactive as reactive


# NOTE: fork of relations.AutoAccessors for forwards compat behaviour
class KeystoneAutoAccessors(type):
    """
    Metaclass that converts fields referenced by ``auto_accessors`` into
    accessor methods with very basic doc strings.
    """

    def __new__(cls, name, parents, dct):
        for field in dct.get('auto_accessors', []):
            meth_name = field.replace('-', '_')
            meth = cls._accessor(field)
            meth.__name__ = meth_name
            meth.__module__ = dct.get('__module__')
            meth.__doc__ = 'Get the %s, if available, or None.' % field
            dct[meth_name] = meth
        return super(KeystoneAutoAccessors, cls).__new__(
            cls, name, parents, dct
        )

    @staticmethod
    def _accessor(field):
        def _accessor_internal(self):
            # Use remapped or transposed key for application
            # data bag lookup for forwards compat
            app_field = self._forward_compat_remaps.get(
                field,
                field.replace('_', '-')
            )
            return self.relations[0].received_app_raw.get(
                app_field,
                self.all_joined_units.received.get(field)
            )
        return _accessor_internal


class KeystoneRequires(reactive.Endpoint, metaclass=KeystoneAutoAccessors):

    auto_accessors = [
        'service_host',
        'service_protocol',
        'service_port',
        'service_tenant',
        'service_username',
        'service_password',
        'service_tenant_id',
        'auth_host',
        'auth_protocol',
        'auth_port',
        'admin_token',
        'ssl_key',
        'ca_cert',
        'ssl_cert',
        'https_keystone',
        'ssl_cert_admin',
        'ssl_cert_internal',
        'ssl_cert_public',
        'ssl_key_admin',
        'ssl_key_internal',
        'ssl_key_public',
        'api_version',
        'service_domain',
        'service_domain_id',
        'ep_changed',
        'admin_domain_id',
        'admin_user_id',
        'admin_project_id',
        'service_type',
        'public-auth-url',
        'internal-auth-url',
        'admin-auth-url',
    ]

    _forward_compat_remaps = {
        'admin_user': 'admin-user-name',
        'service_username': 'service-user-name',
        'service_tenant': 'service-project-name',
        'service_tenant_id': 'service-project-id',
        'service_domain': 'service-domain-name',
    }

    @reactive.when('endpoint.{endpoint_name}.joined')
    def joined(self):
        reactive.set_flag(self.expand_name('{endpoint_name}.connected'))

    @reactive.when('endpoint.{endpoint_name}.changed')
    def changed(self):
        self.update_flags()
        reactive.clear_flag(
            self.expand_name(
                'endpoint.{endpoint_name}.changed'))

    def update_flags(self):
        if self.base_data_complete():
            reactive.set_flag(self.expand_name('{endpoint_name}.available'))
            reactive.set_flag(
                self.expand_name('{endpoint_name}.available.auth'))
            if self.ssl_data_complete():
                reactive.set_flag(
                    self.expand_name('{endpoint_name}.available.ssl'))
            else:
                reactive.clear_flag(
                    self.expand_name('{endpoint_name}.available.ssl'))
            if self.ssl_data_complete_legacy():
                reactive.set_flag(
                    self.expand_name('{endpoint_name}.available.ssl_legacy'))
            else:
                reactive.clear_flag(
                    self.expand_name('{endpoint_name}.available.ssl_legacy'))
        else:
            reactive.clear_flag(
                self.expand_name('{endpoint_name}.available'))
            reactive.clear_flag(
                self.expand_name('{endpoint_name}.available.ssl'))
            reactive.clear_flag(
                self.expand_name('{endpoint_name}.available.ssl_legacy'))
            reactive.clear_flag(
                self.expand_name('{endpoint_name}.available.auth'))

    @reactive.when('endpoint.{endpoint_name}.departed')
    def departed(self):
        self.update_flags()
        reactive.clear_flag(
            self.expand_name(
                'endpoint.{endpoint_name}.departed'))

    def base_data_complete(self):
        data = {
            'service_host': self.service_host(),
            'service_protocol': self.service_protocol(),
            'service_port': self.service_port(),
            'auth_host': self.auth_host(),
            'auth_protocol': self.auth_protocol(),
            'auth_port': self.auth_port(),
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
                           admin_url, requested_roles=None,
                           add_role_to_admin=None,
                           service_type=None,
                           service_description=None):
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
        if requested_roles:
            relation_info.update(
                {'requested_roles': ','.join(requested_roles)})
        if add_role_to_admin:
            relation_info.update(
                {'add_role_to_admin': ','.join(add_role_to_admin)})
        for relation in self.relations:
            relation.to_publish_raw.update(relation_info)

        # NOTE: forwards compatible data presentation for keystone-k8s
        if all((service_type,
                service_description,
                reactive.is_flag_set('leadership.is_leader'),)):
            application_info = {
                'region': region,
                'service-endpoints': json.dumps([
                    {
                        'service_name': service,
                        'type': service_type,
                        'description': service_description,
                        'internal_url': internal_url,
                        'admin_url': admin_url,
                        'public_url': public_url,
                    }
                ], sort_keys=True)
            }
            for relation in self.relations:
                relation.to_publish_app_raw.update(application_info)

    def request_keystone_endpoint_information(self):
        self.register_endpoints('None', 'None', 'None', 'None', 'None')

    def request_notification(self, services):
        """
        Request notification about changes to endpoints

        :param services: services to request notification about
        :type: list[str]
        """
        relation_info = {
            "subscribe_ep_change": " ".join(services),
        }
        for relation in self.relations:
            relation.to_publish_raw.update(relation_info)

    def get_ssl_key(self, cn=None):
        relation_key = 'ssl_key_{}'.format(cn) if cn else 'ssl_key'
        key = self.all_joined_units.received.get(relation_key)
        if key:
            key = base64.b64decode(key).decode('utf-8')
        return key

    def get_ssl_cert(self, cn=None):
        relation_key = 'ssl_cert_{}'.format(cn) if cn else 'ssl_cert'
        cert = self.all_joined_units.received.get(relation_key)
        if cert:
            cert = base64.b64decode(cert).decode('utf-8')
        return cert

    def get_ssl_ca(self, cn=None):
        ca = None
        if self.ca_cert():
            ca = base64.b64decode(self.ca_cert()).decode('utf-8')
        return ca

    def endpoint_checksums(self):
        """Read any endpoint notification checksums from the interface

        :returns: endpoint->checksum data dictionary
        :rtype: dict
        """
        if self.ep_changed():
            return self.ep_changed()
        return {}

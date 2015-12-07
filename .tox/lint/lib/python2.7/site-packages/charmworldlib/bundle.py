import json
import yaml

from . import api
from .charm import Charm


class BundleNotFound(Exception):
    pass


class Bundles(api.API):
    _base_endpoint = {1: 'bundle', 2: 'bundle', 3: 'bundle'}
    _base_search_endpoint = {1: 'bundles', 2: 'search', 3: 'search'}
    _doctype = 'bundle'

    def proof(self, deployer_contents):
        if not self.version >= 3:
            raise ValueError('Need to use charmworld API >= 3, selected: %s' %
                             self.version)
        if type(deployer_contents) is not dict:
            raise Exception('Invalid deployer_contents')

        return self.post('%s/proof' % self._base_endpoint[self.version],
                         {'deployer_file': yaml.dump(deployer_contents)})

    def bundle(self, basket_name, name, revision=None, owner=None):
        data = self.get(self.bundle_endpoint(
            basket_name, name, revision, owner))

        if 'result' not in data:
            return None

        bundle_raw = data['result'][0]
        return Bundle.from_bundledata(bundle_raw)

    def bundle_endpoint(self, basket_name, name, revision=None, owner=None):
        if owner and not owner.startswith('~'):
            owner = "~%s" % owner

        endpoint = self._base_endpoint[self.version]

        if owner:
            endpoint = "%s/%s" % (endpoint, owner)

        endpoint = "%s/%s" % (endpoint, basket_name)

        if isinstance(revision, int) and revision >= 0:
            endpoint = "%s/%s" % (endpoint, revision)

        endpoint = "%s/%s" % (endpoint, name)

        return endpoint

    def search(self, criteria=None, limit=None):
        result = super(Bundles, self).search(
            self._base_search_endpoint[self.version],
            self._doctype,
            criteria=criteria,
            limit=limit)
        return [Bundle.from_bundledata(bundle['bundle']) for bundle in result]

    def approved(self):
        return self.search(criteria={'type': 'approved'})


class Bundle(object):
    @classmethod
    def from_bundledata(cls, bundle_data):
        bundle = cls()
        bundle._parse(bundle_data)

        return bundle

    def __init__(self, bundle_id=None):
        self.charms = {}
        self._raw = {}
        self._api = api.API()

        if bundle_id:
            self._fetch(bundle_id)

    def __getattr__(self, key):
        return self._raw[key]

    def _fetch(self, bundle_id):
        b = Bundles()
        owner, basket_name, revision, name = self._parse_id(bundle_id)
        try:
            data = self._api.get(b.bundle_endpoint(basket_name, name,
                                                   revision=revision,
                                                   owner=owner))
            self._parse(data)
        except Exception as e:
            raise BundleNotFound('API request failed: %s' % str(e))

    def _parse(self, bundle_data):
        self._raw = bundle_data

        for charm_name, charm_data in bundle_data['charm_metadata'].items():
            self.charms[charm_name] = Charm.from_charmdata({
                'charm': charm_data})

    def _parse_id(self, bundle_id):
        owner, revision = None, None

        parts = bundle_id.split('/')

        if len(parts) == 4:
            owner, basket_name, revision, name = parts
        elif len(parts) == 3:
            if bundle_id.startswith('~'):
                owner, basket_name, name = parts
            else:
                basket_name, revision, name = parts
        elif len(parts) == 2:
            basket_name, name = parts
        else:
            raise ValueError('Invalid bundle id: {}'.format(bundle_id))

        if revision:
            revision = int(revision)

        return owner, basket_name, revision, name

    def __str__(self):
        return json.dumps(self._raw, indent=2)

    def __repr__(self):
        return '<Bundle %s>' % self.id

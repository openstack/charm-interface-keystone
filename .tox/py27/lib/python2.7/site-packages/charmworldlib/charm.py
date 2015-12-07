import re
import json
from . import api


class CharmNotFound(Exception):
    pass


def parse_charm_id(charm_id):
    if charm_id.startswith('cs:'):
        charm_id = charm_id.replace('cs:', '')

    if charm_id.startswith('~'):
        if charm_id.count('/') == 1:
            series = 'precise'
            owner, charm_data = charm_id.split('/')
        else:
            owner, series, charm_data = charm_id.split('/')
    else:
        owner = None
        if '/' not in charm_id:
            series = 'precise'
            charm_data = charm_id
        else:
            series, charm_data = charm_id.split('/')

    ver_match = re.search('-([0-9])+$', charm_data)
    if ver_match:
        version = int(ver_match.group(0)[1:])
        charm = charm_data.replace('-%s' % version, '')
    else:
        version = None
        charm = charm_data

    return owner, series, charm, version


class Charms(api.API):
    _base_endpoint = {1: 'charm', 2: 'charm', 3: 'charm'}
    _base_search_endpoint = {1: 'charms', 2: 'charms', 3: 'search'}
    _doctype = 'charm'

    def requires(self, interfaces=[], limit=None):
        return self.interfaces(requires=interfaces)

    def provides(self, interfaces=[], limit=None):
        return self.interfaces(provides=interfaces)

    def interfaces(self, requires=[], provides=[], limit=None):
        params = {}
        if type(requires) == str:
            requires = [requires]
        if type(provides) == str:
            provides = [provides]

        if type(requires) is not list or type(provides) is not list:
            raise Exception('requires/provides must be either a str or list')

        if requires:
            params['requires'] = ','.join(requires)
        if provides:
            params['provides'] = ','.join(provides)

        return self.search(params)

    def charm(self, name, series='precise', revision=None, owner=None):
        data = self.get(self.charm_endpoint(name, series, revision, owner))

        if 'result' not in data:
            return None

        charm_raw = data['result'][0]
        return Charm.from_charmdata(charm_raw)

    def charm_endpoint(self, name, series='precise', revision=None,
                       owner=None):
        if owner and not owner.startswith('~'):
            owner = "~%s" % owner

        endpoint = self._base_endpoint[self.version]

        if owner:
            endpoint = "%s/%s" % (endpoint, owner)

        endpoint = "%s/%s/%s" % (endpoint, series, name)

        if isinstance(revision, int) and revision >= 0:
            endpoint = "%s-%s" % (endpoint, revision)

        return endpoint

    def search(self, criteria=None, limit=None):
        result = super(Charms, self).search(
            self._base_search_endpoint[self.version],
            self._doctype,
            criteria=criteria,
            limit=limit)
        return [Charm.from_charmdata(charm) for charm in result]

    def approved(self):
        return self.search(criteria={'type': 'approved'})


class Charm(object):
    @classmethod
    def from_charmdata(cls, charm_data):
        charm = cls()
        charm._parse(charm_data)

        return charm

    def __init__(self, charm_id=None):
        self.id = None
        self.name = None
        self.owner = None
        self.series = None
        self.maintainer = None
        self.revision = None
        self.summary = None
        self.url = None
        self.approved = False
        self.subordinate = False
        self.categories = None
        self.provides = {}
        self.requires = {}
        self._raw = {}
        self._api = api.API()

        if charm_id:
            self._fetch(charm_id)

    def related(self):
        data = self._api.get('%s/related' % self.id)
        related = {}
        for relation, interfaces in data['result'].items():
            related[relation] = {}
            for interface, charms in interfaces.items():
                related[relation][interface] = []
                for charm in charms:
                    related[relation][interface].append(Charm(charm['id']))

        return related

    def file(self, path):
        if path not in self.files:
            raise IOError(0, 'No such file in charm', path)
        r = self._api.fetch_request('charm/%s/file/%s' % (self.id, path))

        return r.text

    def _fetch(self, charm_id):
        c = Charms()
        owner, series, charm, revision = parse_charm_id(charm_id)
        try:
            data = self._api.get(c.charm_endpoint(charm, series=series,
                                                  owner=owner,
                                                  revision=revision))
            self._parse(data)
        except Exception as e:
            raise CharmNotFound('API request failed: %s' % str(e))

    def _parse(self, charm_data):
        if 'charm' not in charm_data:
            raise CharmNotFound('Not a valid charm payload')

        for key, val in charm_data['charm'].items():
            if key == 'relations':
                for k, v in charm_data['charm']['relations'].items():
                    setattr(self, k, v)

            if key.startswith('is_'):
                key = key.replace('is_', '')

            if key == 'code_source':
                setattr(self, 'source', val)

            if key == 'distro_series':
                key = 'series'

            setattr(self, key, val)

        self._raw = charm_data

    def __str__(self):
        return json.dumps(self._raw, indent=2)

    def __repr__(self):
        return '<Charm %s>' % self.id

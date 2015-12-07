import requests


class MethodMismatch(Exception):
    pass


class API(object):
    def __init__(self, server='manage.jujucharms.com', version=3, secure=True,
                 port=None, proxy_info=None):
        self.server = server
        self.protocol = 'https' if secure else 'http'
        self.port = port
        self.version = version
        self.proxy = proxy_info

    def get(self, endpoint, params={}):
        return self.fetch_json(endpoint, params, 'get')

    def post(self, endpoint, params={}):
        return self.fetch_json(endpoint, params, 'post')

    def fetch_json(self, endpoint, params={}, method='get'):
        r = self.fetch_request(endpoint, params, method)
        if r.status_code is not 200:
            raise Exception('Request failed with: %s' % r.status_code)
        return r.json()

    def fetch_request(self, endpoint, params={}, method='get'):
        method = method.lower()
        if method not in ['get', 'post']:
            raise MethodMismatch('%s is not get or post' % method)

        if method == 'post':
            r = requests.post(self._build_url(endpoint), data=params)
        elif method == 'get':
            r = requests.get(self._build_url(endpoint), params=params)

        return r

    def search(self, endpoint, doctype, criteria=None, limit=None):
        if type(criteria) is str:
            criteria = {'text': criteria}
        else:
            criteria = criteria or {}

        criteria['text'] = self._doctype_filter(criteria.get('text'), doctype)

        if limit and type(limit) is int:
            criteria['limit'] = limit

        return self.get(endpoint, criteria)['result'] or []

    def _earl(self):
        if self.port:
            return '%s://%s:%s' % (self.protocol, self.server, self.port)

        return '%s://%s' % (self.protocol, self.server)

    def _build_url(self, endpoint):
        if not endpoint[0] == '/':
            endpoint = '/%s' % endpoint

        return '%s/api/%s%s' % (self._earl(), self.version, endpoint)

    def _doctype_filter(self, text, doctype):
        text = (text or '').strip()
        if not text:
            return doctype
        if not text.startswith(doctype + ':'):
            return '{}:{}'.format(doctype, text)
        return text

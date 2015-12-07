# Copyright 2009 Canonical Ltd.  All rights reserved.
#
# This file is part of lazr.authenticate
#
# lazr.authenticate is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, version 3 of the
# License.
#
# lazr.authenticate is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lazr.authenticate.  If not, see <http://www.gnu.org/licenses/>.

"""WSGI middleware that handles the server side of HTTP authenticate."""

__metaclass__ = type
__all__ = [
    'AuthenticationMiddleware',
    'BasicAuthMiddleware',
    'OAuthMiddleware',
]

import base64
import re
try:
    from urllib.parse import urlunparse
except ImportError:
    from urlparse import urlunparse

from oauth.oauth import (
    OAuthError, OAuthRequest, OAuthServer, OAuthSignatureMethod_PLAINTEXT)


class AuthenticationMiddleware(object):
    """A base class for middleware that authenticates HTTP requests.

    This class implements a generic HTTP authenticate workflow:
    check whether the requested resource is protected, get credentials
    from the WSGI environment, validate them (using a callback
    function) and either allow or deny acces.

    All subclasses must define the variable AUTH_SCHEME, which is the
    HTTP authentication scheme (eg."Basic", "OAuth"). This string is sent
    along with a HTTP response code of 401 ("Unauthorized").
    """

    def __init__(self, application, authenticate_with,
                 realm="Restricted area", protect_path_pattern='.*'):
        """Constructor.

        :param application: A WSGI application.

        :param authenticate_with: A callback function that takes some
            number of credential arguemnts (the number and type
            depends on the implementation of
            getCredentialsFromEnvironment()) and returns an object
            representing the authenticated user. If the credentials
            are invalid or don't identify any existing user, the
            function should return None.

        :param realm: The string to give out as the authenticate realm.
        :param protect_path_pattern: A regular expression string. URL
            paths matching this string will be protected with the
            authenticate method. URL paths not matching this string
            can be accessed without authenticating.
        """
        self.application = application
        self.authenticate_with = authenticate_with
        self.realm = realm
        self.protect_path_pattern = re.compile(protect_path_pattern)

    def _unauthorized(self, start_response):
        """Short-circuit the request with a 401 error code."""
        start_response("401 Unauthorized",
                       [('WWW-Authenticate',
                         '%s realm="%s"' % (self.AUTH_SCHEME, self.realm))])
        return [b'401 Unauthorized']

    def __call__(self, environ, start_response):
        """Protect certain resources by checking auth credentials."""
        path_info = environ.get('PATH_INFO', '/')
        if not self.protect_path_pattern.match(path_info):
            environ.setdefault('authenticated_user')
            return self.application(environ, start_response)

        try:
            credentials = self.getCredentialsFromEnvironment(environ)
        except ValueError:
            credentials = None
        if credentials is None:
            return self._unauthorized(start_response)

        authenticated_user = self.authenticate_with(*credentials)
        if authenticated_user is None:
            return self._unauthorized(start_response)

        environ['authenticated_user'] = authenticated_user

        return self.application(environ, start_response)

    def getCredentialsFromEnvironment(self, environment):
        """Retrieve a set of credentials from the environment.

        This superclass implementation ignores the environment
        entirely, and so never authenticates anybody.

        :param environment: The WSGI environment.
        :return: A list of objects to be passed into the authenticate_with
                 callback function, or None if the credentials could not
                 be determined.
        """
        return None


class BasicAuthMiddleware(AuthenticationMiddleware):
    """WSGI middleware that implements HTTP Basic Auth."""

    AUTH_SCHEME = "Basic"

    def getCredentialsFromEnvironment(self, environ):
        authorization = environ.get('HTTP_AUTHORIZATION')
        if authorization is None:
            return None

        method, auth = authorization.split(' ', 1)
        if method.lower() != 'basic':
            return None

        auth = base64.b64decode(auth.strip().encode('ascii')).decode()
        username, password = auth.split(':', 1)
        return username, password


class OAuthMiddleware(AuthenticationMiddleware):
    """WSGI middleware that implements (part of) OAuth.

    This middleware only protects resources by making sure requests
    are signed with a valid consumer and access token. It does not
    help clients get request tokens or exchange request tokens for
    access tokens.
    """

    AUTH_SCHEME = "OAuth"

    def __init__(self, application, authenticate_with, data_store=None,
                 realm="Restricted area", protect_path_pattern='.*'):
        """See `AuthenticationMiddleware.`

        :param data_store: An OAuthDataStore.
        """
        super(OAuthMiddleware, self).__init__(
            application, authenticate_with, realm, protect_path_pattern)
        self.data_store = data_store

    def getCredentialsFromEnvironment(self, environ):
        http_method = environ['REQUEST_METHOD']

        # Recreate the URL.
        url_scheme = environ['wsgi.url_scheme']
        hostname = environ['HTTP_HOST']
        path = environ['PATH_INFO']
        query_string = environ.get('QUERY_STRING', '')
        original_url = urlunparse(
            (url_scheme, hostname, path, '', query_string, ''))
        headers = {'Authorization' : environ.get('HTTP_AUTHORIZATION', '')}
        request = OAuthRequest().from_request(
            http_method, original_url, headers=headers,
            query_string=query_string)
        if request is None:
            return None
        server = OAuthServer(self.data_store)
        server.add_signature_method(OAuthSignatureMethod_PLAINTEXT())
        try:
            consumer, token, parameters = server.verify_request(request)
        except OAuthError:
            return None
        return consumer, token, parameters

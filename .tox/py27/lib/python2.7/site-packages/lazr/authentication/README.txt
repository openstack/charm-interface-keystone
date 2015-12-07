..
    This file is part of lazr.authentication.

    lazr.authentication is free software: you can redistribute it and/or modify it
    under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, version 3 of the License.

    lazr.authentication is distributed in the hope that it will be useful, but
    WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
    or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
    License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with lazr.authentication.  If not, see <http://www.gnu.org/licenses/>.

WSGI Middleware
===============

lazr.authentication defines some simple WSGI middleware for protecting
resources with different kinds of HTTP authentication.

    >>> from __future__ import print_function
    >>> import lazr.authentication
    >>> print('VERSION: %s' % lazr.authentication.__version__)
    VERSION: ...


BasicAuthMiddleware
-------------------

The BasicAuthMiddleware implements HTTP Basic Auth. Its constructor
takes a number of arguments, including a callback function that
performs the actual authentication. This function returns an object
identifying the user who's trying to authenticate. If the
authentication credentials are invalid, it's supposed to return None.

First, let's create a really simple WSGI application that responds to
any request with a 200 response code.

    >>> def dummy_application(environ, start_response):
    ...         start_response('200', [('Content-type','text/plain')])
    ...         return [b'Success']

Now let's protect that application. Here's an authentication callback
function.

    >>> def authenticate(username, password):
    ...     """Accepts "user/password", rejects everything else.
    ...
    ...     :return: The username, if the credentials are valid.
    ...              None, otherwise.
    ...     """
    ...     if username == "user" and password == "password":
    ...         return username
    ...     return None

    >>> print(authenticate("user", "password"))
    user

    >>> print(authenticate("notuser", "password"))
    None

Here's a WSGI application that protects the application using
BasicAuthMiddleware.

    >>> from lazr.authentication.wsgi import BasicAuthMiddleware
    >>> def protected_application():
    ...     return BasicAuthMiddleware(
    ...         dummy_application, realm="WSGI middleware test",
    ...         protect_path_pattern=".*protected.*",
    ...         authenticate_with=authenticate)

    >>> import wsgi_intercept
    >>> from wsgi_intercept.httplib2_intercept import install
    >>> install()
    >>> wsgi_intercept.add_wsgi_intercept(
    ...     'basictest', 80, protected_application)

Most of the application's URLs are not protected by the
middleware. You can access them without providing credentials.

    >>> import httplib2
    >>> client = httplib2.Http()
    >>> response, body = client.request('http://basictest/')
    >>> print(response['status'])
    200
    >>> print(body.decode())
    Success

Any URL that includes the string "protected" is protected by the
middleware, and cannot be accessed without credentials.

    >>> response, body = client.request('http://basictest/protected/')
    >>> print(response['status'])
    401
    >>> print(response['www-authenticate'])
    Basic realm="WSGI middleware test"

    >>> response, body = client.request(
    ...     'http://basictest/this-is-protected-as-well/')
    >>> print(response['status'])
    401

The check_credentials() implementation given at the beginning of the
test will only accept the user/password combination "user"/"password".
Provide a bad username or password and you'll get a 401.

    >>> client.add_credentials("baduser", "baspassword")
    >>> response, body = client.request('http://basictest/protected/')
    >>> print(response['status'])
    401

Provide the correct credentials and you'll get a 200, even for the
protected URIs.

    >>> client.add_credentials("user", "password")
    >>> response, body = client.request('http://basictest/protected/')
    >>> print(response['status'])
    200

Teardown.

    >>> wsgi_intercept.remove_wsgi_intercept('basictest', 80)

Stacking
********

BasicAuthMiddleware instances can be stacked, each instance protecting
a different path pattern. Here, we'll use stacking to protect
the two regexes ".*protected.*" and ".*different.*", without combining
them into one complex regex.

    >>> def return_user_application(environ, start_response):
    ...         start_response('200', [('Content-type','text/plain')])
    ...         return [str(environ['authenticated_user']).encode('utf-8')]

    >>> def protected_application():
    ...     protected = BasicAuthMiddleware(
    ...         return_user_application, realm="WSGI middleware test",
    ...         protect_path_pattern=".*protected.*",
    ...         authenticate_with=authenticate)
    ...     return BasicAuthMiddleware(
    ...         protected, realm="Another middleware",
    ...         protect_path_pattern=".*different.*",
    ...         authenticate_with=authenticate)

Setup.

    >>> wsgi_intercept.add_wsgi_intercept(
    ...     'stacked', 80, protected_application)
    >>> client = httplib2.Http()

Both path patterns are protected:

    >>> response, body = client.request('http://stacked/protected')
    >>> print(response['status'])
    401
    >>> response, body = client.request('http://stacked/different')
    >>> print(response['status'])
    401

Both path patterns control respond to the same credentials.

    >>> client.add_credentials("user", "password")

    >>> response, body = client.request('http://stacked/protected-resource')
    >>> print(response['status'])
    200
    >>> print(body.decode())
    user

    >>> response, body = client.request('http://stacked/different-resource')
    >>> print(response['status'])
    200
    >>> print(body.decode())
    user

    >>> wsgi_intercept.remove_wsgi_intercept('stacked', 80)

OAuthMiddleware
---------------

The OAuthMiddleware implements section 7 ("Accessing Protected
Resources") of the OAuth specification. That is, it makes sure that
incoming consumer keys and access tokens pass some application-defined
test. It does not help you serve request tokens or exchange a request
token for an access token.

We'll use OAuthMiddleware to protect the same simple application we
protected earlier with BasicAuthMiddleware. But since we're using
OAuth, we'll be checking a consumer key and access token, instead of a
username and password.

    >>> from oauth.oauth import OAuthConsumer, OAuthToken

    >>> valid_consumer = OAuthConsumer("consumer", '')
    >>> valid_token = OAuthToken("token", "secret")

    >>> def authenticate(consumer, token, parameters):
    ...     """Accepts the valid consumer and token, rejects everything else.
    ...
    ...     :return: The consumer, if the credentials are valid.
    ...              None, otherwise.
    ...     """
    ...     if consumer == valid_consumer and token == valid_token:
    ...         return consumer
    ...     return None

    >>> print(authenticate(valid_consumer, valid_token, None).key)
    consumer

    >>> invalid_consumer = OAuthConsumer("other consumer", '')
    >>> print(authenticate(invalid_consumer, valid_token, None))
    None

To test the OAuthMiddleware's security features, we'll also need to
create a data store. In a real application the data store would
probably be a database containing the registered consumer keys and
tokens. We're using a simple data store designed for testing, and
telling it about the one valid consumer and token.

    >>> from lazr.authentication.testing.oauth import SimpleOAuthDataStore
    >>> data_store = SimpleOAuthDataStore(
    ...     {valid_consumer.key : valid_consumer},
    ...     {valid_token.key : valid_token})

    >>> print(data_store.lookup_consumer("consumer").key)
    consumer
    >>> print(data_store.lookup_consumer("badconsumer"))
    None

The data store tracks the use of OAuth nonces. If you call the data
store's lookup_nonce() twice with the same values, the first call will
return False and the second call will return True.

    >>> print(data_store.lookup_nonce("consumer", "token", "nonce"))
    False
    >>> print(data_store.lookup_nonce("consumer", "token", "nonce"))
    True

    >>> print(data_store.lookup_nonce("newconsumer", "token", "nonce"))
    False

Now let's protect an application with lazr.authenticate's
OAuthMiddleware, using our authentication technique and our simple
data store.

    >>> from lazr.authentication.wsgi import OAuthMiddleware
    >>> def protected_application():
    ...     return OAuthMiddleware(
    ...         dummy_application, realm="OAuth test",
    ...         authenticate_with=authenticate, data_store=data_store)

    >>> wsgi_intercept.add_wsgi_intercept(
    ...     'oauthtest', 80, protected_application)
    >>> client = httplib2.Http()

A properly signed request will go through to the underlying WSGI
application.

    >>> from oauth.oauth import (
    ...     OAuthRequest, OAuthSignatureMethod_PLAINTEXT)
    >>> def sign_request(url, consumer=valid_consumer, token=valid_token):
    ...     request = OAuthRequest().from_consumer_and_token(
    ...         consumer, token, http_url=url)
    ...     request.sign_request(
    ...         OAuthSignatureMethod_PLAINTEXT(), consumer, token)
    ...     headers = request.to_header('OAuth test')
    ...     return headers

    >>> url = 'http://oauthtest/'
    >>> headers = sign_request(url)
    >>> response, body = client.request(url, headers=headers)
    >>> print(response['status'])
    200
    >>> print(body.decode())
    Success

If you replay a signed HTTP request that worked the first time, it
will fail the second time, because you'll be sending a nonce that was
already used.

    >>> response, body = client.request(url, headers=headers)
    >>> print(response['status'])
    401

An unsigned request will fail.

    >>> response, body = client.request('http://oauthtest/')
    >>> print(response['status'])
    401
    >>> print(response['www-authenticate'])
    OAuth realm="OAuth test"

A request signed with invalid credentials will fail.

    >>> bad_token = OAuthToken("token", "badsecret")
    >>> headers = sign_request(url, token=bad_token)
    >>> response, body = client.request(url, headers=headers)
    >>> print(response['status'])
    401

Teardown.

    >>> wsgi_intercept.remove_wsgi_intercept('oauthtest', 80)

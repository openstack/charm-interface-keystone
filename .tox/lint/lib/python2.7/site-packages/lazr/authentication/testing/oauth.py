# Copyright 2009 Canonical Ltd.  All rights reserved.
#
# This file is part of lazr.authentication
#
# lazr.authentication is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, version 3 of the
# License.
#
# lazr.authentication is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with lazr.authentication.  If not, see
# <http://www.gnu.org/licenses/>.

"""Utility classes for testing OAuth authentication."""

__metaclass__ = type
__all__ = [
    'SimpleOAuthDataStore',
]

# Work around relative import behavior.  The below is equivalent to
# from oauth import oauth
oauth = __import__('oauth.oauth', {}).oauth
OAuthDataStore = oauth.OAuthDataStore


class SimpleOAuthDataStore(OAuthDataStore):
    """A very simple implementation of the oauth library's OAuthDataStore."""

    def __init__(self, consumers=None, tokens=None):
        """Initialize with no nonces."""
        self.consumers = consumers or {}
        self.tokens = tokens or {}
        self.nonces = set()

    def lookup_token(self, token_type, token_field):
        """Turn a token key into an OAuthToken object."""
        return self.tokens.get(token_field)

    def lookup_consumer(self, consumer):
        """Turn a consumer key into an OAuthConsumer object."""
        return self.consumers.get(consumer)

    def lookup_nonce(self, consumer, token, nonce):
        """Make sure a nonce has not already been used.

        If the nonce has not been used, add it to the set
        so that a future call to this method will return False.
        """
        key = (consumer, token, nonce)
        if key in self.nonces:
            return True
        self.nonces.add(key)
        return False

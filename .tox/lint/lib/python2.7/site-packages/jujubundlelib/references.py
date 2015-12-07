# Copyright 2015 Canonical Ltd.
# Licensed under the AGPLv3, see LICENCE file for details.

from __future__ import unicode_literals

import re

from jujubundlelib import pyutils


# The URL of jujucharms.com, the home of Juju.
JUJUCHARMS_URL = 'https://jujucharms.com/'

# The following regular expressions are the same used in juju-core: see
# http://bazaar.launchpad.net/~go-bot/juju-core/trunk/view/head:/charm/url.go.
USER_PATTERN = r'[a-z0-9][a-zA-Z0-9+.-]+'
SERIES_PATTERN = r'[a-z]+(?:[a-z-]+[a-z])?'
NAME_PATTERN = r'[a-z][a-z0-9]*(?:-[a-z0-9]*[a-z][a-z0-9]*)*'

# Define the name of the development channel.
DEVELOPMENT_CHANNEL = 'development'

# Define the callables used to check if entity reference components are valid.
valid_user = re.compile(r'^{}$'.format(USER_PATTERN)).match
valid_name = re.compile(r'^{}$'.format(NAME_PATTERN)).match
valid_series = re.compile(r'^{}$'.format(SERIES_PATTERN)).match
valid_channel = lambda channel: channel == DEVELOPMENT_CHANNEL

# Compile the regular expression used to parse new jujucharms entity URLs.
_jujucharms_url_expression = re.compile(r"""
    ^  # Beginning of the line.
    (?:
        (?:{jujucharms})?  # Optional jujucharms.com URL.
        |
        /?  # Optional leading slash.
    )?
    (?:u/({user_pattern})/)?  # Optional user name.
    (?:({development})/)?  # Optional channel.
    ({name_pattern})  # Bundle name.
    (?:/({series_pattern}))?  # Optional series.
    (?:/(\d+))?  # Optional bundle revision number.
    /?  # Optional trailing slash.
    $  # End of the line.
""".format(
    development=DEVELOPMENT_CHANNEL,
    jujucharms=JUJUCHARMS_URL,
    name_pattern=NAME_PATTERN,
    series_pattern=SERIES_PATTERN,
    user_pattern=USER_PATTERN,
), re.VERBOSE)


@pyutils.string_class
class Reference(object):
    """Represent a charm or bundle URL reference."""

    def __init__(self, schema, user, channel, series, name, revision):
        """Initialize the reference. Receives the URL fragments."""
        self.schema = schema
        self.user = user
        self.channel = channel
        self.series = series
        self.name = name
        if revision is not None:
            revision = int(revision)
        self.revision = revision
        # XXX frankban 2015-02-26: remove the following attribute when
        # switching to the new bundle format, and when we have a better way
        # to increase bundle deployments count.
        self.charmworld_id = None

    @classmethod
    def from_string(cls, url):
        """Given an entity URL as a string, create and return a Reference.

        The given URL may be not fully qualified, meaning it can miss
        the schema (in which case "cs:" is inferred), the series
        (defaulting to "") and the revision (set to None if not specified).

        Raise a ValueError if the provided value is not a valid URL.
        """
        return cls(*_parse_url(url, fully_qualified=False))

    @classmethod
    def from_fully_qualified_url(cls, url):
        """Given an entity URL as a string, create and return a Reference.

        Fully qualified URLs represent the regular entity reference
        representation in Juju, e.g.: "cs:`~who/vivid/django-42" or
        "local:bundle/wordpress-0".

        Raise a ValueError if the provided value is not a valid and fully
        qualified URL, also including the schema and the revision.
        """
        return cls(*_parse_url(url, fully_qualified=True))

    @classmethod
    def from_jujucharms_url(cls, url):
        """Create and return a Reference from the given jujucharms.com URL.

        These are the preferred way to refer to a charm or bundle They
        basically look like the URL paths in jujucharms.com,
        e.g. "u/who/django", "mediawiki/42" or just "mediawiki". The full HTTP
        URL can be also provided, for instance "https://jujucharms.com/django".

        Raise a ValueError if the provided URL is not valid.
        """
        match = _jujucharms_url_expression.match(url)
        if match is None:
            msg = 'invalid charm or bundle URL: {}'.format(url)
            raise ValueError(msg.encode('utf-8'))
        user, channel, name, series, revision = match.groups()
        return cls(
            'cs', user or '', channel or '', series or '', name, revision)

    def __str__(self):
        """The string representation of a reference is its URL string."""
        return self.id()

    def __repr__(self):
        return '<Reference: {}>'.format(self)

    def __eq__(self, other):
        """Two refs are equal if they have the same parts."""
        return (
            isinstance(other, self.__class__) and
            self.schema == other.schema and
            self.user == other.user and
            self.channel == other.channel and
            self.series == other.series and
            self.name == other.name and
            self.revision == other.revision
        )

    def path(self):
        """Return the reference as a string without the schema."""
        user = '~{}'.format(self.user) if self.user else ''
        name_revision = self.name
        if self.revision is not None:
            name_revision += '-{}'.format(self.revision)
        return '/'.join(
            filter(None, [user, self.channel, self.series, name_revision]))

    def id(self):
        """Return the reference URL as a string."""
        return '{}:{}'.format(self.schema, self.path())

    def similar(self, other):
        """Report whether the other reference refers to a similar charm.

        Two references are considered similar if they share the same schema,
        user and name.
        Raise a TypeError if the given reference is not a Reference instance.
        """
        if not isinstance(other, self.__class__):
            msg = 'cannot compare unsupported type {}'.format(
                other.__class__.__name__)
            raise TypeError(msg.encode('utf-8'))
        return (
            (self.schema, self.user, self.name) ==
            (other.schema, other.user, other.name))

    def copy(self, **kwargs):
        """Copy this reference.

        If keyword arguments are passed, the copied reference will have the
        corresponding attributes.
        For instance:

            ref = reference.copy()
            ref = reference.copy(revision=42)
            ref = reference.copy(channel='', user='')
        """
        reference = self.__class__(
            self.schema, self.user, self.channel, self.series, self.name,
            self.revision)
        for key, value in kwargs.items():
            setattr(reference, key, value)
        return reference

    def jujucharms_id(self):
        """Return the identifier of this reference in jujucharms.com."""
        user_part = 'u/{}/'.format(self.user) if self.user else ''
        channel_part = '{}/'.format(self.channel) if self.channel else ''
        series_part = '/{}'.format(self.series) if self.series else ''
        revision_part = ''
        if self.revision is not None:
            revision_part = '/{}'.format(self.revision)
        return '{}{}{}{}{}'.format(
            user_part, channel_part, self.name, series_part, revision_part)

    def jujucharms_url(self):
        """Return the URL where this entity lives in jujucharms.com."""
        return JUJUCHARMS_URL + self.jujucharms_id()

    def is_bundle(self):
        """Report whether this reference refers to a bundle entity."""
        return self.series == 'bundle'

    def is_local(self):
        """Return True if this refers to a local entity, False otherwise."""
        return self.schema == 'local'

    def is_fully_qualified(self):
        """Report whether this reference is fully qualified.

        A fully qualified reference includes its schema, series and revision.
        """
        return self.schema and self.series and (self.revision is not None)

    def is_under_development(self):
        """Report whether this reference points to a development entity."""
        return self.channel == DEVELOPMENT_CHANNEL


def _parse_url(url, fully_qualified=False):
    """Parse the given charm or bundle URL, provided as a string.

    Return a tuple containing the entity reference fragments: schema, user,
    channel, series, name and revision.
    Each fragment is a string except revision (int).

    Raise a ValueError with a descriptive message if the given URL is not
    valid. If fully_qualified is True, the URL must include the schema, series
    and revision, otherwise a ValueError is raised.
    """
    # Retrieve the schema.
    try:
        schema, remaining = url.split(':', 1)
    except ValueError:
        if fully_qualified:
            msg = 'URL has no schema: {}'.format(url)
            raise ValueError(msg.encode('utf-8'))
        schema = 'cs'
        remaining = url
    if schema not in ('cs', 'local'):
        msg = 'URL has invalid schema: {}'.format(schema)
        raise ValueError(msg.encode('utf-8'))
    # Retrieve and validate the optional user.
    parts = remaining.split('/')
    part = parts.pop(0)
    user = ''
    if part.startswith('~'):
        user = part[1:]
        if not valid_user(user):
            msg = 'URL has invalid user name: {}'.format(user)
            raise ValueError(msg.encode('utf-8'))
        if schema == 'local':
            msg = 'local entity URL with user name: {}'.format(url)
            raise ValueError(msg.encode('utf-8'))
        if not parts:
            msg = 'URL has invalid form: {}'.format(url)
            raise ValueError(msg.encode('utf-8'))
        part = parts.pop(0)
    # Retrieve and validate the optional channel.
    channel = ''
    if valid_channel(part) and parts:
        channel = part
        if schema == 'local':
            msg = 'local entity URL with channel: {}'.format(url)
            raise ValueError(msg.encode('utf-8'))
        part = parts.pop(0)
    # Retrieve and validate the series.
    series = ''
    if parts:
        series = part
        if not valid_series(series):
            msg = 'URL has invalid series: {}'.format(series)
            raise ValueError(msg.encode('utf-8'))
        part = parts.pop(0)
    elif fully_qualified:
        msg = 'URL has invalid form: {}'.format(url)
        raise ValueError(msg.encode('utf-8'))
    # Retrieve and validate name and revision.
    if parts:
        msg = 'URL has invalid form: {}'.format(url)
        raise ValueError(msg.encode('utf-8'))
    try:
        name, revision = part.rsplit('-', 1)
    except ValueError:
        if fully_qualified:
            msg = 'URL has no revision: {}'.format(url)
            raise ValueError(msg.encode('utf-8'))
        name, revision = part, None
    if revision is not None:
        try:
            revision = int(revision)
        except ValueError:
            if fully_qualified:
                msg = 'URL has invalid revision: {}'.format(revision)
                raise ValueError(msg.encode('utf-8'))
            name, revision = name + '-' + revision, None
    if not valid_name(name):
        msg = 'URL has invalid name: {}'.format(name)
        raise ValueError(msg.encode('utf-8'))
    return schema, user, channel, series, name, revision

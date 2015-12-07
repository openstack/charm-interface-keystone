# Copyright 2015 Canonical Ltd.
# Licensed under the AGPLv3, see LICENCE file for details.

from __future__ import unicode_literals

import unittest

from jujubundlelib import (
    pyutils,
    references,
)
from jujubundlelib.tests import helpers


def make_reference(
        schema='cs', user='myuser', channel='', series='precise',
        name='juju-gui', revision=42):
    """Create and return a Reference instance."""
    return references.Reference(schema, user, channel, series, name, revision)


class TestReference(unittest.TestCase):

    representation_tests = (
        # Fully qualified.
        (make_reference(),
         'cs:~myuser/precise/juju-gui-42'),

        # Fully qualified local.
        (make_reference(schema='local', user=''),
         'local:precise/juju-gui-42'),

        # Promulgated charm.
        (make_reference(user=''),
         'cs:precise/juju-gui-42'),

        # Custom name, series and revision.
        (make_reference(name='django', series='vivid', revision=0),
         'cs:~myuser/vivid/django-0'),

        # No series.
        (make_reference(series=''),
         'cs:~myuser/juju-gui-42'),

        # Promulgated charm without series.
        (make_reference(user='', series=''),
         'cs:juju-gui-42'),

        # No revision.
        (make_reference(user='dalek', revision=None, series='bundle'),
         'cs:~dalek/bundle/juju-gui'),

        # Promulgated charm without revision.
        (make_reference(user='', revision=None),
         'cs:precise/juju-gui'),

        # No series and revision.
        (make_reference(series='', revision=None),
         'cs:~myuser/juju-gui'),

        # Promulgated charm without series and revision.
        (make_reference(user='', series='', revision=None),
         'cs:juju-gui'),

        # Fully qualified under development.
        (make_reference(channel=references.DEVELOPMENT_CHANNEL),
         'cs:~myuser/development/precise/juju-gui-42'),

        # Promulgated charm under development.
        (make_reference(user='', channel=references.DEVELOPMENT_CHANNEL),
         'cs:development/precise/juju-gui-42'),

        # Custom name, series and revision under development.
        (make_reference(
            channel=references.DEVELOPMENT_CHANNEL, name='django',
            series='vivid', revision=0),
         'cs:~myuser/development/vivid/django-0'),

        # No series under development.
        (make_reference(channel=references.DEVELOPMENT_CHANNEL, series=''),
         'cs:~myuser/development/juju-gui-42'),

        # Promulgated charm without series under development.
        (make_reference(
            user='', channel=references.DEVELOPMENT_CHANNEL, series=''),
         'cs:development/juju-gui-42'),

        # Promulgated charm without revision under development.
        (make_reference(
            user='', channel=references.DEVELOPMENT_CHANNEL, revision=None),
         'cs:development/precise/juju-gui'),

        # No series and revision under development.
        (make_reference(
            channel=references.DEVELOPMENT_CHANNEL, series='', revision=None),
         'cs:~myuser/development/juju-gui'),
    )

    jujucharms_tests = (
        (make_reference(),
         'u/myuser/juju-gui/precise/42'),
        (make_reference(schema='local'),
         'u/myuser/juju-gui/precise/42'),
        (make_reference(user=''),
         'juju-gui/precise/42'),
        (make_reference(user='dalek', revision=None, series=''),
         'u/dalek/juju-gui'),
        (make_reference(name='django', series='vivid', revision=0),
         'u/myuser/django/vivid/0'),
        (make_reference(name='django', series='', revision=0),
         'u/myuser/django/0'),
        (make_reference(user='', revision=None),
         'juju-gui/precise'),
        (make_reference(user='', series='', revision=None),
         'juju-gui'),
        (make_reference(channel=references.DEVELOPMENT_CHANNEL),
         'u/myuser/development/juju-gui/precise/42'),
        (make_reference(user='', channel=references.DEVELOPMENT_CHANNEL),
         'development/juju-gui/precise/42'),
        (make_reference(user='dalek', channel=references.DEVELOPMENT_CHANNEL,
                        revision=None, series=''),
         'u/dalek/development/juju-gui'),
        (make_reference(user='dalek', channel=references.DEVELOPMENT_CHANNEL,
                        revision=None, series='bundle'),
         'u/dalek/development/juju-gui/bundle'),
        (make_reference(channel=references.DEVELOPMENT_CHANNEL, name='django',
                        series='vivid', revision=0),
         'u/myuser/development/django/vivid/0'),
        (make_reference(user='', channel=references.DEVELOPMENT_CHANNEL,
                        revision=None),
         'development/juju-gui/precise'),
        (make_reference(user='', channel=references.DEVELOPMENT_CHANNEL,
                        series='', revision=None),
         'development/juju-gui'),
        (make_reference(user='', channel=references.DEVELOPMENT_CHANNEL,
                        series='bundle', revision=None),
         'development/juju-gui/bundle'),
        (make_reference(user='', channel=references.DEVELOPMENT_CHANNEL,
                        series='bundle', revision=0),
         'development/juju-gui/bundle/0'),
    )

    def test_attributes(self):
        # All reference attributes are correctly stored.
        ref = make_reference()
        self.assertEqual('cs', ref.schema)
        self.assertEqual('myuser', ref.user)
        self.assertEqual('', ref.channel)
        self.assertEqual('precise', ref.series)
        self.assertEqual('juju-gui', ref.name)
        self.assertEqual(42, ref.revision)

    def test_revision_as_string(self):
        # The reference revision is converted to an int.
        ref = make_reference(revision='47')
        self.assertEqual(47, ref.revision)

    def test_string(self):
        # The string representation of a reference is its URL.
        for ref, expected_value in self.representation_tests:
            self.assertEqual(expected_value, str(ref))

    def test_repr(self):
        # A reference is correctly represented.
        for ref, expected_value in self.representation_tests:
            expected_value = '<Reference: {}>'.format(expected_value)
            self.assertEqual(expected_value, repr(ref))

    def test_path(self):
        # The reference path is properly returned as a URL string without the
        # schema.
        for ref, expected_value in self.representation_tests:
            expected_value = expected_value.split(':', 1)[1]
            self.assertEqual(expected_value, ref.path())

    def test_id(self):
        # The reference id is correctly returned.
        for ref, expected_value in self.representation_tests:
            self.assertEqual(expected_value, ref.id())

    def test_copy(self):
        # The reference can be correctly copied.
        ref = make_reference()
        copied_ref = ref.copy()
        self.assertIsNot(ref, copied_ref)
        self.assertEqual(ref, copied_ref)

    def test_copy_with_attributes(self):
        # The reference can be copied overriding specific attributes.
        ref = make_reference()
        copy1 = ref.copy(channel=references.DEVELOPMENT_CHANNEL)
        copy2 = ref.copy(user='', series='wily', revision=0)
        self.assertNotEqual(ref, copy1)
        self.assertNotEqual(ref, copy2)
        self.assertEqual('cs:~myuser/precise/juju-gui-42', str(ref))
        self.assertEqual(
            'cs:~myuser/development/precise/juju-gui-42', str(copy1))
        self.assertEqual('cs:wily/juju-gui-0', str(copy2))

    def test_jujucharms_id(self):
        # It is possible to return the reference identifier in jujucharms.com.
        for ref, expected_value in self.jujucharms_tests:
            self.assertEqual(expected_value, ref.jujucharms_id())

    def test_jujucharms_url(self):
        # The corresponding charm or bundle page in jujucharms.com is correctly
        # returned.
        for ref, expected_value in self.jujucharms_tests:
            expected_url = references.JUJUCHARMS_URL + expected_value
            self.assertEqual(expected_url, ref.jujucharms_url())

    def test_charm_entity(self):
        # The is_bundle method returns False for charm references.
        ref = make_reference(series='vivid')
        self.assertFalse(ref.is_bundle())

    def test_bundle_entity(self):
        # The is_bundle method returns True for bundle references.
        ref = make_reference(series='bundle')
        self.assertTrue(ref.is_bundle())

    def test_charm_store_entity(self):
        # The is_local method returns False for charm store references.
        ref = make_reference(schema='cs')
        self.assertFalse(ref.is_local())

    def test_local_entity(self):
        # The is_local method returns True for local references.
        ref = make_reference(schema='local')
        self.assertTrue(ref.is_local())

    def test_equality(self):
        # Two references are equal if they have the same URL.
        self.assertEqual(make_reference(), make_reference())
        self.assertEqual(make_reference(user=''), make_reference(user=''))
        self.assertEqual(
            make_reference(channel=references.DEVELOPMENT_CHANNEL),
            make_reference(channel=references.DEVELOPMENT_CHANNEL))
        self.assertEqual(
            make_reference(revision=None), make_reference(revision=None))

    def test_equality_different_references(self):
        # Two references with different attributes are not equal.
        tests = (
            (make_reference(schema='cs'),
             make_reference(schema='local')),
            (make_reference(user=''),
             make_reference(user='who')),
            (make_reference(),
             make_reference(channel=references.DEVELOPMENT_CHANNEL)),
            (make_reference(series='trusty'),
             make_reference(series='vivid')),
            (make_reference(name='django'),
             make_reference(name='rails')),
            (make_reference(revision=0),
             make_reference(revision=1)),
            (make_reference(revision=None),
             make_reference(revision=42)),
        )
        for ref1, ref2 in tests:
            self.assertNotEqual(ref1, ref2)

    def test_equality_different_types(self):
        # A reference never equals a non-reference object.
        self.assertNotEqual(make_reference(), 42)
        self.assertNotEqual(make_reference(), True)
        self.assertNotEqual(make_reference(), 'oranges')

    def test_charmworld_id(self):
        # By default, the reference id in charmworld is set to None.
        # XXX frankban 2015-02-26: remove this test once we get rid of the
        # charmworld id concept.
        ref = make_reference()
        self.assertIsNone(ref.charmworld_id)

    def test_is_fully_qualified(self):
        # True is returned if the reference is fully qualified.
        self.assertTrue(make_reference().is_fully_qualified())
        self.assertTrue(make_reference(schema='local').is_fully_qualified())
        self.assertTrue(make_reference(user='').is_fully_qualified())
        self.assertTrue(make_reference(
            channel=references.DEVELOPMENT_CHANNEL).is_fully_qualified())
        self.assertTrue(make_reference(revision=0).is_fully_qualified())

    def test_is_not_fully_qualified(self):
        # False is returned if the reference is not fully qualified.
        self.assertFalse(make_reference(series='').is_fully_qualified())
        self.assertFalse(make_reference(revision=None).is_fully_qualified())

    def test_is_under_development(self):
        # True is returned if the reference is under development.
        self.assertTrue(make_reference(
            channel=references.DEVELOPMENT_CHANNEL).is_under_development())
        self.assertTrue(make_reference(
            user='',
            channel=references.DEVELOPMENT_CHANNEL).is_under_development())
        self.assertTrue(make_reference(
            channel=references.DEVELOPMENT_CHANNEL,
            revision=0).is_under_development())

    def test_is_not_under_development(self):
        # False is returned if the reference is not under development.
        self.assertFalse(make_reference(schema='local').is_under_development())
        self.assertFalse(make_reference(series='').is_under_development())
        self.assertFalse(make_reference(revision=None).is_under_development())


class TestReferenceSimilar(unittest.TestCase):

    def test_similar_references(self):
        # True is returned if the references are similar.
        ref = make_reference()
        self.assertTrue(ref.similar(make_reference()))
        self.assertTrue(ref.similar(make_reference(
            channel=references.DEVELOPMENT_CHANNEL)))
        self.assertTrue(ref.similar(make_reference(series='utopic')))
        self.assertTrue(
            ref.similar(make_reference(series='trusty', revision=0)))

    def test_similar_promulgated_references(self):
        # True is returned if the promulgated references are similar.
        ref = make_reference(user='')
        self.assertTrue(ref.similar(ref))
        self.assertTrue(ref.similar(make_reference(user='', series='utopic')))
        self.assertTrue(ref.similar(make_reference(
            user='', channel=references.DEVELOPMENT_CHANNEL)))
        self.assertTrue(
            ref.similar(make_reference(user='', series='trusty', revision=0)))

    def test_different_references(self):
        # False is returned if the references do not share the same schema,
        # user or name.
        ref = make_reference()
        self.assertFalse(ref.similar(make_reference(schema='local')))
        self.assertFalse(ref.similar(make_reference(user='who')))
        self.assertFalse(ref.similar(make_reference(name='django')))

    def test_different_promulgated_references(self):
        # False is returned if the promulgated references do not share the
        # same schema, user or name.
        ref = make_reference(user='')
        self.assertFalse(ref.similar(make_reference(schema='local', user='')))
        self.assertFalse(ref.similar(make_reference(user='who')))
        self.assertFalse(ref.similar(make_reference(user='', name='django')))

    def test_different_types(self):
        # A type error is returned if an unsupported type is provided.
        ref = make_reference()
        with self.assertRaises(TypeError) as ctx:
            ref.similar(42)
        self.assertEqual(
            'cannot compare unsupported type int',
            pyutils.exception_string(ctx.exception))


class TestReferenceFromFullyQualifiedUrl(
        helpers.ValueErrorTestsMixin, unittest.TestCase):

    def test_no_schema_error(self):
        # A ValueError is raised if the URL schema is missing.
        expected_error = b'URL has no schema: precise/juju-gui'
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url('precise/juju-gui')

    def test_no_url_error(self):
        # A ValueError is raised if the URL is empty.
        expected_error = b'URL has no schema: '
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url('')

    def test_invalid_schema_error(self):
        # A ValueError is raised if the URL schema is not valid.
        expected_error = b'URL has invalid schema: http'
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url(
                'http:precise/juju-gui')

    def test_invalid_user_name_error(self):
        # A ValueError is raised if the user name is not valid.
        expected_error = b'URL has invalid user name: jean:luc'
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url(
                'cs:~jean:luc/precise/juju-gui')

    def test_local_user_name_error(self):
        # A ValueError is raised if a user is specified on a local entity.
        expected_error = (
            b'local entity URL with user name: '
            b'local:~jean-luc/precise/juju-gui')
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url(
                'local:~jean-luc/precise/juju-gui')

    def test_invalid_channel_error(self):
        # A ValueError is raised if the channel is not valid.
        expected_error = (
            b'URL has invalid form: cs:~jean-luc/bad-wolf/wily/juju-gui')
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url(
                'cs:~jean-luc/bad-wolf/wily/juju-gui')

    def test_local_channel_error(self):
        # A ValueError is raised if a channel is specified on a local entity.
        expected_error = (
            b'local entity URL with channel: '
            b'local:development/precise/juju-gui')
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url(
                'local:development/precise/juju-gui')

    def test_invalid_form_error(self):
        # A ValueError is raised if the URL is not valid.
        expected_error = (
            b'URL has invalid form: cs:~user/development/series/name/what-?')
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url(
                'cs:~user/development/series/name/what-?')

    def test_user_only_error(self):
        # A ValueError is raised if the URL only includes the user.
        expected_error = (
            b'URL has invalid form: cs:~user')
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url('cs:~user')

    def test_invalid_series_error(self):
        # A ValueError is raised if the series is not valid.
        expected_error = b'URL has invalid series: boo!'
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url(
                'cs:boo!/juju-gui-42')

    def test_no_series_error(self):
        # A ValueError is raised if the series is not specified.
        expected_error = b'URL has invalid form: cs:~user/juju-gui-42'
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url(
                'cs:~user/juju-gui-42')

    def test_no_revision_error(self):
        # A ValueError is raised if the entity revision is missing.
        expected_error = b'URL has no revision: cs:series/name'
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url('cs:series/name')

    def test_invalid_revision_error(self):
        # A ValueError is raised if the charm or bundle revision is not valid.
        expected_error = b'URL has invalid revision: revision'
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url(
                'cs:series/name-revision')

    def test_invalid_name_error(self):
        # A ValueError is raised if the entity name is not valid.
        expected_error = b'URL has invalid name: not:valid'
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url(
                'cs:precise/not:valid-42')

    def test_success(self):
        # References are correctly instantiated by parsing the fully qualified
        # URL.
        tests = (
            ('cs:~myuser/precise/juju-gui-42',
             make_reference()),
            ('cs:trusty/juju-gui-42',
             make_reference(user='', series='trusty')),
            ('local:precise/juju-gui-42',
             make_reference(schema='local', user='')),
            ('cs:~myuser/development/precise/juju-gui-42',
             make_reference(channel=references.DEVELOPMENT_CHANNEL)),
            ('cs:development/trusty/juju-gui-42',
             make_reference(user='', channel=references.DEVELOPMENT_CHANNEL,
                            series='trusty')),
        )
        for url, expected_ref in tests:
            ref = references.Reference.from_fully_qualified_url(url)
            self.assertEqual(expected_ref, ref)


class TestReferenceFromString(
        helpers.ValueErrorTestsMixin, unittest.TestCase):

    def test_invalid_schema_error(self):
        # A ValueError is raised if the URL schema is not valid.
        expected_error = b'URL has invalid schema: http'
        with self.assert_value_error(expected_error):
            references.Reference.from_string('http:precise/juju-gui')

    def test_no_url_error(self):
        # A ValueError is raised if the URL is empty.
        expected_error = b'URL has no schema: '
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url('')

    def test_invalid_user_name_error(self):
        # A ValueError is raised if the user name is not valid.
        expected_error = b'URL has invalid user name: jean:luc'
        with self.assert_value_error(expected_error):
            references.Reference.from_string(
                'cs:~jean:luc/precise/juju-gui')

    def test_local_user_name_error(self):
        # A ValueError is raised if a user is specified on a local entity.
        expected_error = (
            b'local entity URL with user name: '
            b'local:~jean-luc/precise/juju-gui')
        with self.assert_value_error(expected_error):
            references.Reference.from_string(
                'local:~jean-luc/precise/juju-gui')

    def test_invalid_channel_error(self):
        # A ValueError is raised if the channel is not valid.
        expected_error = (
            b'URL has invalid form: cs:~jean-luc/bad-wolf/wily/juju-gui')
        with self.assert_value_error(expected_error):
            references.Reference.from_string(
                'cs:~jean-luc/bad-wolf/wily/juju-gui')

    def test_local_channel_error(self):
        # A ValueError is raised if a channel is specified on a local entity.
        expected_error = (
            b'local entity URL with channel: '
            b'local:development/precise/juju-gui')
        with self.assert_value_error(expected_error):
            references.Reference.from_string(
                'local:development/precise/juju-gui')

    def test_invalid_form_error(self):
        # A ValueError is raised if the URL is not valid.
        expected_error = b'URL has invalid form: cs:~user/series/name/what-?'
        with self.assert_value_error(expected_error):
            references.Reference.from_string(
                'cs:~user/series/name/what-?')

    def test_user_only_error(self):
        # A ValueError is raised if the URL only includes the user.
        expected_error = (
            b'URL has invalid form: cs:~user')
        with self.assert_value_error(expected_error):
            references.Reference.from_string('cs:~user')

    def test_invalid_series_error(self):
        # A ValueError is raised if the series is not valid.
        expected_error = b'URL has invalid series: boo!'
        with self.assert_value_error(expected_error):
            references.Reference.from_string(
                'cs:boo!/juju-gui-42')

    def test_invalid_name_error(self):
        # A ValueError is raised if the entity name is not valid.
        expected_error = b'URL has invalid name: not:valid'
        with self.assert_value_error(expected_error):
            references.Reference.from_string(
                'cs:precise/not:valid-42')

    def test_success(self):
        # References are correctly instantiated by parsing the URL.
        tests = (
            # Fully qualified.
            ('cs:~myuser/precise/juju-gui-42',
             make_reference()),

            # Fully qualified and promulgated.
            ('cs:trusty/juju-gui-42',
             make_reference(user='', series='trusty')),

            # Fully qualified local.
            ('local:precise/juju-gui-42',
             make_reference(schema='local', user='')),

            # No schema.
            ('~myuser/precise/juju-gui-42',
             make_reference()),

            # No schema and promulgated.
            ('trusty/juju-gui-42',
             make_reference(user='', series='trusty')),

            # No series.
            ('cs:~myuser/juju-gui-42',
             make_reference(series='')),

            # No series and promulgated.
            ('cs:juju-gui-42',
             make_reference(user='', series='')),

            # No revision.
            ('cs:~myuser/precise/juju-gui',
             make_reference(revision=None)),

            # No revision and not hyphen in name.
            ('cs:~myuser/precise/django',
             make_reference(name='django', revision=None)),

            # No revision and promulgated.
            ('cs:precise/juju-gui',
             make_reference(user='', revision=None)),

            # No schema, series and revision.
            ('~myuser/juju-gui',
             make_reference(series='', revision=None)),

            # No schema, series and revision, promulgated.
            ('juju-gui',
             make_reference(user='', series='', revision=None)),

            # Fully qualified (under development).
            ('cs:~myuser/development/precise/juju-gui-42',
             make_reference(channel=references.DEVELOPMENT_CHANNEL)),

            # Fully qualified and promulgated (under development).
            ('cs:development/trusty/juju-gui-42',
             make_reference(user='', channel=references.DEVELOPMENT_CHANNEL,
                            series='trusty')),

            # No schema (under development).
            ('~myuser/development/precise/juju-gui-42',
             make_reference(channel=references.DEVELOPMENT_CHANNEL)),

            # No schema and promulgated (under development).
            ('development/trusty/juju-gui-42',
             make_reference(user='', channel=references.DEVELOPMENT_CHANNEL,
                            series='trusty')),

            # No series (under development).
            ('cs:~myuser/development/juju-gui-42',
             make_reference(channel=references.DEVELOPMENT_CHANNEL,
                            series='')),

            # No series and promulgated (under development).
            ('cs:development/juju-gui-42',
             make_reference(user='', channel=references.DEVELOPMENT_CHANNEL,
                            series='')),

            # No revision (under development).
            ('cs:~myuser/development/precise/juju-gui',
             make_reference(channel=references.DEVELOPMENT_CHANNEL,
                            revision=None)),

            # No revision and not hyphen in name (under development).
            ('cs:~myuser/development/precise/django',
             make_reference(channel=references.DEVELOPMENT_CHANNEL,
                            name='django', revision=None)),

            # No revision and promulgated (under development).
            ('cs:development/precise/juju-gui',
             make_reference(user='', channel=references.DEVELOPMENT_CHANNEL,
                            revision=None)),

            # No schema, series and revision (under development).
            ('~myuser/development/juju-gui',
             make_reference(channel=references.DEVELOPMENT_CHANNEL, series='',
                            revision=None)),

            # No schema, series and revision, promulgated (under development).
            ('development/juju-gui',
             make_reference(user='', channel=references.DEVELOPMENT_CHANNEL,
                            series='', revision=None)),
        )
        for url, expected_ref in tests:
            ref = references.Reference.from_string(url)
            self.assertEqual(expected_ref, ref)


class TestReferenceFromJujucharmsUrl(
        helpers.ValueErrorTestsMixin, unittest.TestCase):

    def test_invalid_form(self):
        # A ValueError is raised if the URL is not valid.
        expected_error = b'invalid charm or bundle URL: bad wolf'
        with self.assert_value_error(expected_error):
            references.Reference.from_jujucharms_url('bad wolf')

    def test_invalid_channel(self):
        # A ValueError is raised if the channel is not valid.
        url = 'u/myuser/bad-wolf/django/trusty/42'
        expected_error = b'invalid charm or bundle URL: ' + url.encode('utf-8')
        with self.assert_value_error(expected_error):
            references.Reference.from_jujucharms_url(url)

    def test_success(self):
        # A reference is correctly created from a jujucharms.com identifier or
        # complete URL.
        tests = (
            # Check with both user and revision.
            ('u/myuser/mediawiki/42',
             make_reference(series='', name='mediawiki')),
            ('/u/myuser/mediawiki/42',
             make_reference(series='', name='mediawiki')),
            ('u/myuser/django-scalable/42/',
             make_reference(series='', name='django-scalable')),
            ('{}u/myuser/mediawiki/42'.format(references.JUJUCHARMS_URL),
             make_reference(series='', name='mediawiki')),
            ('{}u/myuser/mediawiki/42/'.format(references.JUJUCHARMS_URL),
             make_reference(series='', name='mediawiki')),
            ('u/myuser/django-scalable/bundle/42/',
             make_reference(series='bundle', name='django-scalable')),
            ('{}u/myuser/django/bundle/0/'.format(references.JUJUCHARMS_URL),
             make_reference(series='bundle', name='django', revision=0)),

            # Check under development.
            ('u/myuser/development/mediawiki/42',
             make_reference(channel=references.DEVELOPMENT_CHANNEL,
                            series='', name='mediawiki')),
            ('/development/mediawiki/42',
             make_reference(user='', channel=references.DEVELOPMENT_CHANNEL,
                            series='', name='mediawiki')),
            ('development/django-scalable',
             make_reference(user='', channel=references.DEVELOPMENT_CHANNEL,
                            series='', name='django-scalable',
                            revision=None)),
            ('development/django-scalable/bundle',
             make_reference(user='', channel=references.DEVELOPMENT_CHANNEL,
                            series='bundle', name='django-scalable',
                            revision=None)),
            ('u/myuser/development/mediawiki/wily',
             make_reference(channel=references.DEVELOPMENT_CHANNEL,
                            series='wily', name='mediawiki', revision=None)),
            ('/development/mediawiki/trusty/0',
             make_reference(user='', channel=references.DEVELOPMENT_CHANNEL,
                            series='trusty', name='mediawiki', revision=0)),
            ('{}u/myuser/development/hp/42'.format(references.JUJUCHARMS_URL),
             make_reference(channel=references.DEVELOPMENT_CHANNEL,
                            series='', name='hp')),
            ('{}development/mediawiki/42/'.format(references.JUJUCHARMS_URL),
             make_reference(user='', channel=references.DEVELOPMENT_CHANNEL,
                            series='', name='mediawiki')),
            ('development/openstack-base/bundle/47/',
             make_reference(user='', channel=references.DEVELOPMENT_CHANNEL,
                            series='bundle', name='openstack-base',
                            revision=47)),

            # Check without revision.
            ('u/myuser/mediawiki',
             make_reference(series='', name='mediawiki', revision=None)),
            ('/u/myuser/wordpress',
             make_reference(series='', name='wordpress', revision=None)),
            ('u/myuser/mediawiki/',
             make_reference(series='', name='mediawiki', revision=None)),
            ('{}u/myuser/django'.format(references.JUJUCHARMS_URL),
             make_reference(series='', name='django', revision=None)),
            ('{}u/myuser/mediawiki/'.format(references.JUJUCHARMS_URL),
             make_reference(series='', name='mediawiki', revision=None)),
            ('{}u/myuser/mediawiki/bundle/'.format(references.JUJUCHARMS_URL),
             make_reference(series='bundle', name='mediawiki', revision=None)),

            # Check without the user.
            ('rails-single/42',
             make_reference(user='', series='', name='rails-single')),
            ('/mediawiki/42',
             make_reference(user='', series='', name='mediawiki')),
            ('rails-scalable/42/',
             make_reference(user='', series='', name='rails-scalable')),
            ('{}mediawiki/42'.format(references.JUJUCHARMS_URL),
             make_reference(user='', series='', name='mediawiki')),
            ('{}django/42/'.format(references.JUJUCHARMS_URL),
             make_reference(user='', series='', name='django')),
            ('{}django/bundle/42/'.format(references.JUJUCHARMS_URL),
             make_reference(user='', series='bundle', name='django')),

            # Check without user and revision.
            ('mediawiki',
             make_reference(user='', series='', name='mediawiki',
                            revision=None)),
            ('/wordpress',
             make_reference(user='', series='', name='wordpress',
                            revision=None)),
            ('mediawiki/',
             make_reference(user='', series='', name='mediawiki',
                            revision=None)),
            ('{}django'.format(references.JUJUCHARMS_URL),
             make_reference(user='', series='', name='django', revision=None)),
            ('{}mediawiki/'.format(references.JUJUCHARMS_URL),
             make_reference(user='', series='', name='mediawiki',
                            revision=None)),
            ('mediawiki/bundle',
             make_reference(user='', series='bundle', name='mediawiki',
                            revision=None)),
            ('{}django/bundle/'.format(references.JUJUCHARMS_URL),
             make_reference(user='', series='bundle', name='django',
                            revision=None)),

            # Check with charm series.
            ('mediawiki/trusty/0',
             make_reference(user='', series='trusty', name='mediawiki',
                            revision=0)),
            ('/wordpress/precise',
             make_reference(user='', series='precise', name='wordpress',
                            revision=None)),
            ('u/who/rails/vivid',
             make_reference(user='who', series='vivid', name='rails',
                            revision=None)),
        )
        for url, expected_ref in tests:
            ref = references.Reference.from_jujucharms_url(url)
            self.assertEqual(expected_ref, ref)
